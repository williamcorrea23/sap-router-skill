"""CPI archive validation must reject ambiguous and unsafe ZIP entries."""
import io
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGER = ROOT / "scripts" / "cpi_iflow_packager.py"


def make_archive(path: Path, extra_entries=()):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("META-INF/MANIFEST.MF", "Bundle-SymbolicName: fixture\nBundle-Version: 1.0.0\n")
        archive.writestr("src/main/resources/flow.xml", "<IntegrationFlow />")
        for name, body in extra_entries:
            archive.writestr(name, body)


class CpiZipIntegrityTest(unittest.TestCase):
    def validate(self, path):
        return subprocess.run(
            [sys.executable, str(PACKAGER), "validate", "--input", str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_duplicate_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            archive = Path(raw) / "duplicate.zip"
            make_archive(archive, [("META-INF/MANIFEST.MF", "Bundle-SymbolicName: shadow\n")])
            result = self.validate(archive)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate", (result.stdout + result.stderr).lower())

    def test_traversal_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            archive = Path(raw) / "traversal.zip"
            make_archive(archive, [("../../outside.txt", "outside")])
            result = self.validate(archive)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("path", (result.stdout + result.stderr).lower())


if __name__ == "__main__":
    unittest.main()
