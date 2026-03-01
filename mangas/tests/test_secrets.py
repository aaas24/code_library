"""Secrets tests — mock the op CLI subprocess, no real 1Password calls."""
import subprocess
from unittest.mock import MagicMock, patch

import pytest


def test_get_secret_calls_op_cli(mocker, tmp_path):
    """get_secret() calls `op read` with the correct vault path."""
    secrets_yaml = """\
onepassword:
  vault: Private
  item: "Manga - Homelab Server"
  fields:
    pi_host:
      field: "pi_host"
      description: "Pi IP"
      required: true
  ssh:
    item: "SSH Key - Homelab"
    private_key_field: "private key"
    public_key_field: "public key"
"""
    config_file = tmp_path / "secrets.config.yaml"
    config_file.write_text(secrets_yaml)

    import utils.secrets as secrets_mod
    secrets_mod._secrets_config = None  # reset cache
    mocker.patch.object(secrets_mod, "_SECRETS_CONFIG_PATH", config_file)

    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = MagicMock(stdout="192.168.1.100\n", returncode=0)

    result = secrets_mod.get_secret("pi_host")
    assert result == "192.168.1.100"

    call_args = mock_run.call_args[0][0]
    assert call_args[0] == "op"
    assert call_args[1] == "read"
    assert "op://Private/Manga - Homelab Server/pi_host" in call_args[2]


def test_get_secret_missing_key(mocker, tmp_path):
    """Missing key raises KeyError with a helpful message."""
    secrets_yaml = """\
onepassword:
  vault: Private
  item: "Manga - Homelab Server"
  fields: {}
  ssh:
    item: "SSH Key - Homelab"
    private_key_field: "private key"
    public_key_field: "public key"
"""
    config_file = tmp_path / "secrets.config.yaml"
    config_file.write_text(secrets_yaml)

    import utils.secrets as secrets_mod
    secrets_mod._secrets_config = None
    mocker.patch.object(secrets_mod, "_SECRETS_CONFIG_PATH", config_file)

    with pytest.raises(KeyError, match="not defined"):
        secrets_mod.get_secret("nonexistent_key")


def test_get_secret_op_cli_failure(mocker, tmp_path):
    """CalledProcessError from op CLI raises RuntimeError."""
    secrets_yaml = """\
onepassword:
  vault: Private
  item: "Manga - Homelab Server"
  fields:
    flask_secret_key:
      field: "flask_secret_key"
      required: true
  ssh:
    item: "SSH Key - Homelab"
    private_key_field: "private key"
    public_key_field: "public key"
"""
    config_file = tmp_path / "secrets.config.yaml"
    config_file.write_text(secrets_yaml)

    import utils.secrets as secrets_mod
    secrets_mod._secrets_config = None
    mocker.patch.object(secrets_mod, "_SECRETS_CONFIG_PATH", config_file)

    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "op", stderr="item not found"),
    )

    with pytest.raises(RuntimeError, match="Failed to read secret"):
        secrets_mod.get_secret("flask_secret_key")


def test_get_secret_op_not_installed(mocker, tmp_path):
    """FileNotFoundError (op not installed) raises RuntimeError."""
    secrets_yaml = """\
onepassword:
  vault: Private
  item: "Manga - Homelab Server"
  fields:
    pi_host:
      field: "pi_host"
      required: true
  ssh:
    item: "SSH Key - Homelab"
    private_key_field: "private key"
    public_key_field: "public key"
"""
    config_file = tmp_path / "secrets.config.yaml"
    config_file.write_text(secrets_yaml)

    import utils.secrets as secrets_mod
    secrets_mod._secrets_config = None
    mocker.patch.object(secrets_mod, "_SECRETS_CONFIG_PATH", config_file)
    mocker.patch("subprocess.run", side_effect=FileNotFoundError)

    with pytest.raises(RuntimeError, match="op.*not found"):
        secrets_mod.get_secret("pi_host")
