import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

BANK_NAME = "Banco Arits"
CURRENCY_SYMBOL = "$"

DATA_FILE = "accounts.json"
ACCOUNTS_DIR = "cuentas"
LOG_FILE = "log_seguridad.txt"

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"

BG_MAIN       = "#1a1a2e"
BG_SECONDARY  = "#16213e"   
BG_CARD       = "#0f3460"   
ACCENT        = "#00b4d8"   
ACCENT_HOVER  = "#0096c7"  
TEXT_PRIMARY  = "#ffffff"   
TEXT_SECONDARY= "#a8b2d8"   
TEXT_ERROR    = "#e63946"   
TEXT_SUCCESS  = "#2dc653"   
TEXT_WARNING  = "#f4a261"   
FONT_TITLE    = ("Segoe UI", 22, "bold")
FONT_SUBTITLE = ("Segoe UI", 14, "bold")
FONT_NORMAL   = ("Segoe UI", 11)
FONT_SMALL    = ("Segoe UI", 9)
FONT_BTN      = ("Segoe UI", 11, "bold")

ADMIN_USER = "admin"
_admin_pwd = os.getenv("ADMIN_PASSWORD")
if not _admin_pwd:
    raise RuntimeError("Falta la ADMIN_PASSWORD en el archivo .env")

LIMITE_RETIRO_DIARIO        = 1500
LIMITE_TRANSFERENCIA_DIARIA = 1000

EMAIL_REMITENTE = os.getenv("EMAIL_REMITENTE")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")
EMAIL_ADMIN     = os.getenv("EMAIL_ADMIN")