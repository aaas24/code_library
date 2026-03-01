"""One-time setup: creates all required 1Password entries for the manga tracker.

Run once on your computer when first setting up the project:
    python utils/setup_secrets.py
"""
import subprocess
import sys
from pathlib import Path

import yaml

SECRETS_CONFIG = Path(__file__).parent.parent / "secrets.config.yaml"


def _run_op(*args) -> tuple[bool, str]:
    """Run an op CLI command. Returns (success, output)."""
    try:
        result = subprocess.run(
            ["op"] + list(args),
            capture_output=True,
            text=True,
        )
        return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except FileNotFoundError:
        return False, "op CLI not found"


def check_op_installed() -> bool:
    ok, _ = _run_op("--version")
    return ok


def check_signed_in() -> bool:
    ok, _ = _run_op("whoami")
    return ok


def check_item_exists(vault: str, item: str) -> bool:
    ok, _ = _run_op("item", "get", item, "--vault", vault)
    return ok


def get_existing_fields(vault: str, item: str) -> list[str]:
    ok, output = _run_op("item", "get", item, "--vault", vault, "--format", "json")
    if not ok:
        return []
    import json
    try:
        data = json.loads(output)
        return [f.get("label", "") for f in data.get("fields", [])]
    except Exception:
        return []


def create_field(vault: str, item: str, field: str, value: str) -> bool:
    ok, out = _run_op(
        "item", "edit", item,
        f"{field}={value}",
        "--vault", vault,
    )
    return ok


def main():
    print("=== Manga Tracker — 1Password Setup ===\n")

    if not check_op_installed():
        print("ERROR: 1Password CLI (op) is not installed.")
        print("Install it from: https://developer.1password.com/docs/cli/")
        sys.exit(1)
    print("✓ op CLI found")

    if not check_signed_in():
        print("ERROR: Not signed in to 1Password CLI. Run: op signin")
        sys.exit(1)
    print("✓ Signed in to 1Password")

    with open(SECRETS_CONFIG, encoding="utf-8") as f:
        config = yaml.safe_load(f)["onepassword"]

    vault = config["vault"]
    item = config["item"]
    fields = config.get("fields", {})

    if not check_item_exists(vault, item):
        print(f"\nERROR: Item '{item}' not found in vault '{vault}'.")
        print("Create it manually in 1Password, then re-run this script.")
        sys.exit(1)
    print(f"✓ Item '{item}' found in vault '{vault}'")

    existing_fields = get_existing_fields(vault, item)
    print(f"\nExisting fields: {existing_fields}\n")

    for key, meta in fields.items():
        field_name = meta["field"]
        required = meta.get("required", True)
        description = meta.get("description", "")
        example = meta.get("example", "")

        if field_name in existing_fields:
            print(f"  ✓ {field_name} — already exists")
            continue

        if not required:
            print(f"  ~ {field_name} — optional, skipping")
            continue

        print(f"\n  Missing: {field_name}")
        print(f"  {description}")
        if example:
            print(f"  Example: {example}")
        value = input(f"  Enter value for '{field_name}': ").strip()
        if not value:
            print(f"  Skipping (no value entered)")
            continue

        if create_field(vault, item, field_name, value):
            print(f"  ✓ Created '{field_name}'")
        else:
            print(f"  ✗ Failed to create '{field_name}'")

    # Check SSH key
    ssh = config.get("ssh", {})
    ssh_item = ssh.get("item", "")
    if ssh_item:
        if check_item_exists(vault, ssh_item):
            print(f"\n✓ SSH key item '{ssh_item}' found")
        else:
            print(f"\nWARNING: SSH key item '{ssh_item}' not found in vault '{vault}'.")
            print("Create an SSH Key item type in 1Password and name it accordingly.")

    print("\n=== Next steps ===")
    print("1. Add OP_SERVICE_ACCOUNT_TOKEN to your Pi's ~/.bashrc")
    print("2. Add OP_SERVICE_ACCOUNT_TOKEN as a GitHub Actions secret")
    print("3. Run: python import/parse_mangas_md.py")


if __name__ == "__main__":
    main()
