#!/usr/bin/env python3
"""
First-run configuration wizard for d42j platform.
"""
import json
import os
import getpass
from pathlib import Path
from cryptography.fernet import Fernet


def generate_encryption_key():
    """Generate a new encryption key for sensitive data."""
    return Fernet.generate_key()


def encrypt_value(value: str, key: bytes) -> str:
    """Encrypt a sensitive value."""
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()


def get_input(prompt: str, default: str = None, secret: bool = False) -> str:
    """Get user input with optional default and secret handling."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    if secret:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)

    return value.strip() or default


def main():
    """Run the configuration wizard."""
    print("=" * 60)
    print("d42j - Infrastructure Asset Management Platform")
    print("First-Run Configuration Wizard")
    print("=" * 60)
    print()

    config = {}

    # Generate encryption key
    print("Generating encryption key for sensitive data...")
    encryption_key = generate_encryption_key()

    # Device42 Configuration
    print("\n--- Device42 Configuration ---")
    config["device42"] = {
        "host": get_input("Device42 hostname or IP", "rhmd42"),
        "protocol": get_input("Protocol (http/https)", "https"),
        "port": int(get_input("Port", "443")),
        "username": get_input("Device42 username"),
        "password": get_input("Device42 password", secret=True),
        "verify_ssl": get_input("Verify SSL certificates? (yes/no)", "yes").lower() == "yes"
    }

    # Encrypt password
    config["device42"]["password"] = encrypt_value(
        config["device42"]["password"],
        encryption_key
    )

    # Jira Configuration
    print("\n--- Jira ServiceDesk Configuration ---")
    config["jira"] = {
        "host": get_input("Jira URL (e.g., https://jira.company.com)"),
        "username": get_input("Jira username/email"),
        "api_token": get_input("Jira API token", secret=True),
        "project_key": get_input("Jira project key for infrastructure", "IT")
    }

    # Encrypt API token
    config["jira"]["api_token"] = encrypt_value(
        config["jira"]["api_token"],
        encryption_key
    )

    # Risk Assessment Configuration
    print("\n--- Risk Assessment Configuration ---")
    config["risk_assessment"] = {
        "max_age_years": int(get_input("Maximum acceptable age (years)", "7")),
        "age_thresholds": {
            "low": int(get_input("Low risk threshold (years)", "3")),
            "medium": int(get_input("Medium risk threshold (years)", "5")),
            "high": int(get_input("High risk threshold (years)", "7"))
        },
        "failure_rate_model": "bathtub_curve",
        "weight_factors": {
            "age": 0.4,
            "support_status": 0.3,
            "incident_history": 0.2,
            "manufacturer_eol": 0.1
        }
    }

    # Manufacturer API Configuration
    print("\n--- Manufacturer API Configuration ---")
    print("(Leave blank to skip, can be configured later)")
    config["manufacturers"] = {}

    for vendor in ["dell", "hp", "cisco", "juniper", "netapp", "vmware"]:
        enabled = get_input(f"Enable {vendor.upper()} API integration? (yes/no)", "no")
        if enabled.lower() == "yes":
            api_key = get_input(f"{vendor.upper()} API key", secret=True)
            config["manufacturers"][vendor] = {
                "enabled": True,
                "api_key": encrypt_value(api_key, encryption_key) if api_key else ""
            }
        else:
            config["manufacturers"][vendor] = {"enabled": False, "api_key": ""}

    # Cache Configuration
    config["cache"] = {
        "enabled": True,
        "ttl_hours": int(get_input("Cache TTL (hours)", "6"))
    }

    # Server Configuration
    print("\n--- Server Configuration ---")
    config["server"] = {
        "host": get_input("Server bind address", "0.0.0.0"),
        "port": int(get_input("Server port", "8000")),
        "cors_origins": [
            "http://localhost:3000",
            get_input("GitHub Pages URL (e.g., https://username.github.io)", "")
        ]
    }

    # Save configuration
    config_path = Path(__file__).parent / "config.json"
    key_path = Path(__file__).parent / ".encryption_key"

    print(f"\nSaving configuration to {config_path}...")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Saving encryption key to {key_path}...")
    with open(key_path, "wb") as f:
        f.write(encryption_key)

    # Set secure permissions
    os.chmod(config_path, 0o600)
    os.chmod(key_path, 0o600)

    print("\n" + "=" * 60)
    print("Configuration completed successfully!")
    print("=" * 60)
    print(f"\nConfiguration saved to: {config_path}")
    print(f"Encryption key saved to: {key_path}")
    print("\n⚠️  IMPORTANT: Keep these files secure and do not commit them to git!")
    print("\nYou can now start the server with: python main.py")
    print()


if __name__ == "__main__":
    main()
