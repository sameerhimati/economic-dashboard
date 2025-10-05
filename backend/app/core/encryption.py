"""
Encryption utilities for sensitive data.

Provides functions to encrypt and decrypt sensitive data like email passwords
using Fernet symmetric encryption from the cryptography library.
"""
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Custom exception for encryption/decryption errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


def _get_encryption_key() -> bytes:
    """
    Get encryption key from settings.

    Returns:
        bytes: Encryption key

    Raises:
        EncryptionError: If encryption key is not configured
    """
    # For now, use SECRET_KEY as encryption key
    # In production, you might want a separate ENCRYPTION_KEY environment variable
    if not hasattr(settings, 'SECRET_KEY') or not settings.SECRET_KEY:
        raise EncryptionError("SECRET_KEY not configured. Cannot encrypt/decrypt data.")

    # Derive a valid Fernet key from SECRET_KEY
    # Fernet requires a 32 url-safe base64-encoded bytes
    # We'll use the first 32 bytes of SECRET_KEY and base64 encode it
    import base64
    import hashlib

    # Create a consistent 32-byte key from SECRET_KEY using SHA-256
    key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()

    # Base64 encode to make it URL-safe (Fernet requirement)
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_string(plaintext: str) -> str:
    """
    Encrypt a string using Fernet symmetric encryption.

    Args:
        plaintext: String to encrypt

    Returns:
        str: Encrypted string (base64 encoded)

    Raises:
        EncryptionError: If encryption fails
    """
    if not plaintext:
        return ""

    try:
        encryption_key = _get_encryption_key()
        fernet = Fernet(encryption_key)

        # Encrypt the plaintext
        encrypted_bytes = fernet.encrypt(plaintext.encode('utf-8'))

        # Return as string
        return encrypted_bytes.decode('utf-8')

    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}", exc_info=True)
        raise EncryptionError(
            f"Failed to encrypt data: {str(e)}",
            original_error=e
        )


def decrypt_string(encrypted: str) -> str:
    """
    Decrypt a string that was encrypted with encrypt_string.

    Args:
        encrypted: Encrypted string (base64 encoded)

    Returns:
        str: Decrypted plaintext string

    Raises:
        EncryptionError: If decryption fails or token is invalid
    """
    if not encrypted:
        return ""

    try:
        encryption_key = _get_encryption_key()
        fernet = Fernet(encryption_key)

        # Decrypt the data
        decrypted_bytes = fernet.decrypt(encrypted.encode('utf-8'))

        # Return as string
        return decrypted_bytes.decode('utf-8')

    except InvalidToken as e:
        logger.error("Invalid encryption token - data may be corrupted or key changed")
        raise EncryptionError(
            "Failed to decrypt data: invalid encryption token. "
            "Data may be corrupted or encryption key may have changed.",
            original_error=e
        )
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}", exc_info=True)
        raise EncryptionError(
            f"Failed to decrypt data: {str(e)}",
            original_error=e
        )


def encrypt_email_password(password: str) -> Optional[str]:
    """
    Convenience function to encrypt an email password.

    Args:
        password: Email password to encrypt

    Returns:
        Optional[str]: Encrypted password or None if input is None/empty
    """
    if not password:
        return None

    return encrypt_string(password)


def decrypt_email_password(encrypted_password: str) -> Optional[str]:
    """
    Convenience function to decrypt an email password.

    Args:
        encrypted_password: Encrypted email password

    Returns:
        Optional[str]: Decrypted password or None if input is None/empty
    """
    if not encrypted_password:
        return None

    return decrypt_string(encrypted_password)
