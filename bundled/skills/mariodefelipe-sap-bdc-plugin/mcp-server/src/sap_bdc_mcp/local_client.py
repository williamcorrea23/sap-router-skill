"""Local Databricks client that works without dbutils for local development."""

import os
import re
from typing import Any

from bdc_connect_sdk.auth.databricks_client import (
    DatabricksClient,
    _is_brownfield_environment,
)


class LocalDatabricksClient(DatabricksClient):
    """
    A DatabricksClient implementation that works without dbutils.

    This client allows you to use the SAP BDC Connect SDK in local development
    environments where dbutils is not available. It accepts workspace URL and
    API token directly instead of extracting them from the Databricks notebook context.

    Args:
        workspace_url: Databricks workspace URL (e.g., https://dbc-xxxxx.cloud.databricks.com)
        api_token: Databricks personal access token
        recipient_name: Name of the Databricks recipient (optional)
        secrets: Dictionary of secrets for Databricks Connect mode (optional)

    Example:
        ```python
        client = LocalDatabricksClient(
            workspace_url="https://dbc-a413df6c-f111.cloud.databricks.com",
            api_token="dapi...",
            recipient_name="bdc-connect-35c0d016"
        )
        ```
    """

    def __init__(
        self,
        workspace_url: str,
        api_token: str,
        recipient_name: str | None = None,
        secrets: dict[str, str] | None = None,
    ) -> None:
        # Store credentials that would normally come from dbutils
        self.databricks_workspace_url = workspace_url
        self.databricks_api_token = api_token
        self.recipient_name = recipient_name

        # Store secrets for Databricks Connect mode
        self._secrets = secrets or {}

        # Set dbutils to None (not used in local mode)
        self.dbutils = None  # type: ignore

        # Initialize the brownfield detection
        # This determines if we're using BDC Connect (brownfield) or Databricks Connect
        self.is_brownfield_environment = _is_brownfield_environment(
            self.recipient_name,
            self.databricks_workspace_url,
            self.databricks_api_token,
        )

        # Initialize other attributes (same as parent class)
        self.bdc_connect_endpoint = ""
        self.bdc_connect_tenant = ""
        self.bdc_connect_access_token_information: dict[str, str] = {
            "share_url": "",
            "client_id": "",
            "share_location": "",
        }

    def _get_secret(self, secret: str) -> str:
        """
        Get a secret value for Databricks Connect mode.

        In local mode, secrets are read from:
        1. The secrets dict passed to __init__
        2. Environment variables (BDC_SECRET_<SECRET_NAME>)
        3. The .env file (BDC_SECRET_<SECRET_NAME>)

        Args:
            secret: Name of the secret (e.g., "api_url", "tenant", "token_audience")

        Returns:
            The secret value

        Raises:
            ValueError: If the secret is not found and required for Databricks Connect mode
        """
        # Try to get from secrets dict first
        if secret in self._secrets:
            return self._secrets[secret]

        # Try environment variable
        env_key = f"BDC_SECRET_{secret.upper()}"
        env_value = os.getenv(env_key)
        if env_value:
            return env_value

        # If we're in brownfield mode, secrets are not needed
        if self.is_brownfield_environment:
            raise RuntimeError(
                f"Secret '{secret}' requested but not provided. "
                f"This should not happen in brownfield (BDC Connect) mode. "
                f"Please report this as a bug."
            )

        # In Databricks Connect mode, secrets are required
        raise ValueError(
            f"Secret '{secret}' is required for Databricks Connect mode but not found.\n"
            f"You are using Databricks Connect mode (not BDC Connect/brownfield mode).\n"
            f"Please provide secrets via one of these methods:\n"
            f"1. Pass secrets dict to LocalDatabricksClient(..., secrets={{'api_url': '...', 'tenant': '...', ...}})\n"
            f"2. Set environment variable: {env_key}\n"
            f"3. Add to .env file: {env_key}=your_value\n"
            f"\n"
            f"Required secrets for Databricks Connect mode:\n"
            f"  - api_url: BDC Connect API endpoint\n"
            f"  - tenant: BDC Connect tenant name\n"
            f"  - token_audience: Token audience for OIDC authentication"
        )

    @classmethod
    def from_env(cls, env_prefix: str = "DATABRICKS") -> "LocalDatabricksClient":
        """
        Create a LocalDatabricksClient from environment variables.

        Expected environment variables:
        - {prefix}_HOST or {prefix}_WORKSPACE_URL: Workspace URL
        - {prefix}_TOKEN or {prefix}_API_TOKEN: Personal access token
        - {prefix}_RECIPIENT_NAME: Recipient name (optional)

        For Databricks Connect mode secrets:
        - BDC_SECRET_API_URL
        - BDC_SECRET_TENANT
        - BDC_SECRET_TOKEN_AUDIENCE

        Args:
            env_prefix: Prefix for environment variables (default: "DATABRICKS")

        Returns:
            Configured LocalDatabricksClient instance

        Raises:
            ValueError: If required environment variables are missing
        """
        # Get workspace URL
        workspace_url = (
            os.getenv(f"{env_prefix}_HOST")
            or os.getenv(f"{env_prefix}_WORKSPACE_URL")
        )
        if not workspace_url:
            raise ValueError(
                f"Workspace URL not found. Set {env_prefix}_HOST or {env_prefix}_WORKSPACE_URL"
            )

        # Get API token
        api_token = (
            os.getenv(f"{env_prefix}_TOKEN")
            or os.getenv(f"{env_prefix}_API_TOKEN")
        )
        if not api_token:
            raise ValueError(
                f"API token not found. Set {env_prefix}_TOKEN or {env_prefix}_API_TOKEN"
            )

        # Get recipient name (optional)
        recipient_name = os.getenv(f"{env_prefix}_RECIPIENT_NAME")

        # Collect any BDC secrets from environment
        secrets = {}
        for key, value in os.environ.items():
            if key.startswith("BDC_SECRET_"):
                secret_name = key[len("BDC_SECRET_"):].lower()
                secrets[secret_name] = value

        return cls(
            workspace_url=workspace_url,
            api_token=api_token,
            recipient_name=recipient_name,
            secrets=secrets if secrets else None,
        )
