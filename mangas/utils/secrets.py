"""Central secrets interface. All modules call get_secret("key") — never op CLI directly.

Reads secrets.config.yaml to determine the 1Password path, then calls:
    op read "op://<vault>/<item>/<field>"
"""
import subprocess
from pathlib import Path

import yaml

_SECRETS_CONFIG_PATH = Path(__file__).parent.parent / "secrets.config.yaml"
_secrets_config: dict | None = None


def _load_secrets_config() -> dict:
    global _secrets_config
    if _secrets_config is None:
        with open(_SECRETS_CONFIG_PATH, encoding="utf-8") as f:
            _secrets_config = yaml.safe_load(f)
    return _secrets_config


def get_secret(key: str) -> str:
    """Fetch a secret value from 1Password by logical key name.

    Raises:
        KeyError: if the key is not defined in secrets.config.yaml
        RuntimeError: if the op CLI call fails
    """
    config = _load_secrets_config()
    op_cfg = config["onepassword"]
    fields = op_cfg.get("fields", {})

    if key not in fields:
        raise KeyError(
            f"Secret key '{key}' is not defined in secrets.config.yaml. "
            f"Known keys: {list(fields.keys())}"
        )

    field_name = fields[key]["field"]
    vault = op_cfg["vault"]
    item = op_cfg["item"]
    op_path = f"op://{vault}/{item}/{field_name}"

    try:
        result = subprocess.run(
            ["op", "read", op_path],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to read secret '{key}' from 1Password.\n"
            f"  Path: {op_path}\n"
            f"  Error: {e.stderr.strip()}"
        ) from e
    except FileNotFoundError:
        raise RuntimeError(
            "1Password CLI (op) not found. Install it from https://developer.1password.com/docs/cli/"
        )


def get_ssh_private_key() -> str:
    """Fetch the SSH private key from 1Password."""
    config = _load_secrets_config()
    op_cfg = config["onepassword"]
    ssh = op_cfg["ssh"]
    vault = op_cfg["vault"]
    item = ssh["item"]
    field = ssh["private_key_field"]

    try:
        result = subprocess.run(
            ["op", "item", "get", item, "--fields", field, "--vault", vault],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to read SSH private key from 1Password.\n"
            f"  Error: {e.stderr.strip()}"
        ) from e
