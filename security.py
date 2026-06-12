import os
import hashlib
from datetime import datetime
from config import LOG_FILE, ADMIN_USER, _admin_pwd

def hash_password(pwd: str, salt_hex: str = None):
    if salt_hex is None:
        salt = os.urandom(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt, 200_000)
    return key.hex(), salt_hex

def verify_password(pwd: str, stored_hash: str, stored_salt: str) -> bool:
    key, _ = hash_password(pwd, stored_salt)
    return key == stored_hash

def log_sospechoso(evento: str, user: str = "desconocido"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha}] | USUARIO: {user:<10} | EVENTO: {evento}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea)

def get_admin_password_hash():
    return hash_password(_admin_pwd)