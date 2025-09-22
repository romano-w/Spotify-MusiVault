import secrets


def generate_secret_key():
    """Generate a 32-character hexadecimal secret key."""
    return secrets.token_hex(16)


if __name__ == "__main__":
    key = generate_secret_key()
    print("Generated Secret Key:", key)
