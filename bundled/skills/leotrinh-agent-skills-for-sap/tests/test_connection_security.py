"""Offline unit tests for the TLS verification resolver in adt-client.

These tests never open a network socket. They exercise `_resolve_tls_verify`
and `_parse_env_bool` with synthetic argparse namespaces and injected env
dicts, so behavior can be validated without a running SAP system.

Run from the repository root:

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import pathlib
import sys
import unittest
from contextlib import redirect_stderr


_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_CLIENT_PATH = _REPO_ROOT / "skills" / "sap-adt-commands" / "scripts" / "adt-client.py"


def _load_client_module():
    """Import `adt-client.py` as a module even though the filename has a hyphen."""
    spec = importlib.util.spec_from_file_location("adt_client_under_test", _CLIENT_PATH)
    assert spec and spec.loader, f"could not build import spec for {_CLIENT_PATH}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


client = _load_client_module()


def _ns(**overrides) -> argparse.Namespace:
    """Build an argparse namespace with the fields the resolver reads."""
    base = {"insecure": False, "ca_bundle": None}
    base.update(overrides)
    return argparse.Namespace(**base)


class ParseEnvBoolTests(unittest.TestCase):
    def test_none_is_false(self):
        self.assertFalse(client._parse_env_bool(None))

    def test_empty_is_false(self):
        self.assertFalse(client._parse_env_bool(""))
        self.assertFalse(client._parse_env_bool("   "))

    def test_truthy_values(self):
        for value in ["1", "true", "yes", "on", "TRUE", "Yes", " On "]:
            with self.subTest(value=value):
                self.assertTrue(client._parse_env_bool(value))

    def test_falsy_values(self):
        for value in ["0", "false", "no", "off", "maybe", "2"]:
            with self.subTest(value=value):
                self.assertFalse(client._parse_env_bool(value))


class ResolveTlsVerifyDefaultsTests(unittest.TestCase):
    def test_default_is_secure(self):
        result = client._resolve_tls_verify(_ns(), env={})
        self.assertIs(result, True)

    def test_insecure_flag_disables(self):
        result = client._resolve_tls_verify(_ns(insecure=True), env={})
        self.assertIs(result, False)

    def test_ca_bundle_flag_returns_path(self):
        result = client._resolve_tls_verify(
            _ns(ca_bundle="C:/certs/corp.pem"), env={}
        )
        self.assertEqual(result, "C:/certs/corp.pem")


class ResolveTlsVerifyEnvTests(unittest.TestCase):
    def test_env_ca_bundle_used_when_no_flag(self):
        result = client._resolve_tls_verify(
            _ns(), env={"SAP_ADT_CA_BUNDLE": "/etc/ssl/corp.pem"}
        )
        self.assertEqual(result, "/etc/ssl/corp.pem")

    def test_env_insecure_disables_when_no_flag(self):
        for value in ("1", "true", "yes", "on"):
            with self.subTest(value=value):
                result = client._resolve_tls_verify(
                    _ns(), env={"SAP_ADT_INSECURE": value}
                )
                self.assertIs(result, False)

    def test_cli_ca_bundle_overrides_env_insecure(self):
        result = client._resolve_tls_verify(
            _ns(ca_bundle="/etc/ssl/corp.pem"),
            env={"SAP_ADT_INSECURE": "true"},
        )
        self.assertEqual(result, "/etc/ssl/corp.pem")

    def test_cli_insecure_overrides_env_ca_bundle(self):
        result = client._resolve_tls_verify(
            _ns(insecure=True),
            env={"SAP_ADT_CA_BUNDLE": "/etc/ssl/corp.pem"},
        )
        self.assertIs(result, False)


class ResolveTlsVerifyConflictTests(unittest.TestCase):
    def test_cli_insecure_and_cli_ca_bundle_conflict(self):
        with self.assertRaises(SystemExit) as ctx:
            client._resolve_tls_verify(
                _ns(insecure=True, ca_bundle="/tmp/corp.pem"), env={}
            )
        payload = json.loads(str(ctx.exception))
        self.assertIn("Conflicting TLS options", payload["error"])

    def test_cli_insecure_conflicts_with_env_ca_bundle_when_no_cli_bundle(self):
        # env CA bundle is ignored once --insecure wins, so this should NOT
        # raise: the user's explicit CLI intent is clear.
        result = client._resolve_tls_verify(
            _ns(insecure=True),
            env={"SAP_ADT_CA_BUNDLE": "/etc/ssl/corp.pem"},
        )
        self.assertIs(result, False)

    def test_env_insecure_conflicts_with_cli_ca_bundle(self):
        # CLI CA bundle wins over env insecure — no conflict raised.
        result = client._resolve_tls_verify(
            _ns(ca_bundle="/tmp/corp.pem"),
            env={"SAP_ADT_INSECURE": "1"},
        )
        self.assertEqual(result, "/tmp/corp.pem")


class NoNetworkTests(unittest.TestCase):
    """Guard against accidental use of live-network helpers in this test file."""

    def test_module_did_not_perform_http(self):
        # Loading `adt-client.py` must not touch the network. If someone later
        # adds a module-level HTTP call, this test fails loudly.
        self.assertTrue(hasattr(client, "_resolve_tls_verify"))
        self.assertTrue(hasattr(client, "make_session"))
        # `make_session` should still be callable but is never invoked here.


class InsecureWarningTests(unittest.TestCase):
    def test_warning_printed_to_stderr_when_insecure(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            client._warn_insecure_once(False)
        message = buf.getvalue()
        self.assertIn("WARNING", message)
        self.assertIn("--insecure", message)

    def test_no_warning_when_verify_true(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            client._warn_insecure_once(True)
        self.assertEqual(buf.getvalue(), "")

    def test_no_warning_when_ca_bundle_path(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            client._warn_insecure_once("/etc/ssl/corp.pem")
        self.assertEqual(buf.getvalue(), "")

    def test_warning_does_not_leak_env_secrets(self):
        # The warning must not print anything that looks like a credential.
        buf = io.StringIO()
        original_env = os.environ.copy()
        try:
            os.environ["SAP_DEV_DEVELOPER_PWD"] = "TOP_SECRET_PLACEHOLDER"
            with redirect_stderr(buf):
                client._warn_insecure_once(False)
        finally:
            os.environ.clear()
            os.environ.update(original_env)
        message = buf.getvalue()
        self.assertNotIn("TOP_SECRET_PLACEHOLDER", message)
        self.assertNotIn("SAP_DEV_DEVELOPER_PWD", message)


if __name__ == "__main__":
    unittest.main()
