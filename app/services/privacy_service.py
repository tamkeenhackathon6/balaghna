from __future__ import annotations

import base64
import hashlib
import hmac

from cryptography.fernet import Fernet

from app.config import get_settings


def _key_material() -> bytes:
    secret = get_settings().secret_key.encode("utf-8")
    return hashlib.sha256(secret).digest()


def national_id_hash(national_id: str) -> str:
    return hmac.new(_key_material(), national_id.strip().encode("utf-8"), hashlib.sha256).hexdigest()


def encrypt_national_id(national_id: str) -> str:
    key = base64.urlsafe_b64encode(_key_material())
    return Fernet(key).encrypt(national_id.strip().encode("utf-8")).decode("utf-8")


def decrypt_national_id(encrypted_value: str | None) -> str | None:
    if not encrypted_value:
        return None
    key = base64.urlsafe_b64encode(_key_material())
    return Fernet(key).decrypt(encrypted_value.encode("utf-8")).decode("utf-8")
