"""
Configuration loader with encryption support.
"""
import json
from pathlib import Path
from typing import Dict, Any
from cryptography.fernet import Fernet


class ConfigLoader:
    """Load and decrypt configuration."""

    def __init__(self, config_path: str = "config.json", key_path: str = ".encryption_key"):
        self.config_path = Path(config_path)
        self.key_path = Path(key_path)
        self._config = None
        self._cipher = None

    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                "Run 'python configure.py' to create it."
            )

        with open(self.config_path, "r") as f:
            self._config = json.load(f)

        # Load encryption key if it exists
        if self.key_path.exists():
            with open(self.key_path, "rb") as f:
                key = f.read()
                self._cipher = Fernet(key)

        return self._config

    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt an encrypted value."""
        if not self._cipher:
            raise ValueError("Encryption key not loaded")

        return self._cipher.decrypt(encrypted_value.encode()).decode()

    def get(self, path: str, default: Any = None) -> Any:
        """Get a configuration value by path (e.g., 'device42.host')."""
        if not self._config:
            self.load()

        keys = path.split(".")
        value = self._config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default

            if value is None:
                return default

        return value

    def get_decrypted(self, path: str) -> str:
        """Get and decrypt a configuration value."""
        encrypted = self.get(path)
        if encrypted:
            return self.decrypt(encrypted)
        return ""

    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration."""
        if not self._config:
            self.load()
        return self._config
