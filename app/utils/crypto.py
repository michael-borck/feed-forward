"""
Cryptography utilities for securing sensitive data
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Get the secret key from environment variable or use a default for development
# In production, this should be set in the environment
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', 'development-key-please-change-in-production')

def get_encryption_key():
    """
    Derive a Fernet key from the application's SECRET_KEY
    """
    # Use PBKDF2 to derive a key from the secret
    salt = b'feedforward_salt'  # This should be stored securely in production
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_KEY.encode()))
    return key

def encrypt_sensitive_data(data):
    """
    Encrypt sensitive data like API keys before storing in database
    """
    if not data:
        return data
        
    key = get_encryption_key()
    f = Fernet(key)
    # Convert data to bytes if it's a string
    if isinstance(data, str):
        data = data.encode()
    # Encrypt the data
    encrypted_data = f.encrypt(data)
    # Return as base64 encoded string for storage
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_sensitive_data(encrypted_data):
    """
    Decrypt sensitive data for use in API calls
    """
    if not encrypted_data:
        return encrypted_data
        
    key = get_encryption_key()
    f = Fernet(key)
    # Convert from base64 string to bytes
    encrypted_bytes = base64.b64decode(encrypted_data)
    # Decrypt the data
    decrypted_data = f.decrypt(encrypted_bytes)
    # Return as string
    return decrypted_data.decode('utf-8')