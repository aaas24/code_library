from __future__ import annotations

import os
import subprocess
from typing import Optional


REBRICKABLE_TOKEN_REF = "op://Private/Rebrickable/Saved on rebrickable.com/token"


def _read_op_secret(secret_ref: str) -> str:
    try:
        out = subprocess.check_output(["op", "read", secret_ref], text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("1Password CLI 'op' not found. Install and sign in.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Failed to read secret via 1Password CLI. Ensure you are signed in.") from exc
    return out.strip()


def get_rebrickable_token(env_var: str = "REBRICKABLE_API_KEY") -> str:
    token = os.environ.get(env_var)
    if token:
        return token
    token = _read_op_secret(REBRICKABLE_TOKEN_REF)
    os.environ[env_var] = token
    return token


def get_rebrickable_headers() -> dict[str, str]:
    token = get_rebrickable_token()
    return {"Authorization": f"key {token}"}


def try_get_rebrickable_token() -> Optional[str]:
    try:
        return get_rebrickable_token()
    except RuntimeError:
        return None
