import secrets

def generate_secret_key():
    # Generate a 32-character hexadecimal secret key
    secret_key = secrets.token_hex(16)
    return secret_key

if __name__ == "__main__":
    key = generate_secret_key()
    print("Generated Secret Key:", key)
