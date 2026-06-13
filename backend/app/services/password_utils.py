import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{salt}${hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 600000).hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hsh = stored.split("$", 1)
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000).hex() == hsh
    except (ValueError, AttributeError):
        return False
