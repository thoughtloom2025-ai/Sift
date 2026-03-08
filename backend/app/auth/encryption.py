import logging
from cryptography.fernet import Fernet
from app.config import settings

logger = logging.getLogger(__name__)


def get_fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY
    if not key:
        logger.warning("ENCRYPTION_KEY not set — using generated key. Set it in production!")
        key = Fernet.generate_key().decode()
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def encrypt_token(token: str) -> str:
    if not token:
        return token
    f = get_fernet()
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    if not encrypted:
        return encrypted
    try:
        f = get_fernet()
        return f.decrypt(encrypted.encode()).decode()
    except Exception as e:
        logger.error(f"Token decryption failed: {e}")
        return ""
