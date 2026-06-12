import time
from config import YELLOW, RED, GREEN, BOLD, RESET
from security import hash_password, verify_password, log_sospechoso
from display import header, wait, validate_username, parse_integer_amount
from data import record, save_data, save_user_file

def create_account(accounts: dict):
    header("Crear cuenta nueva")
    user = input("Nombre de usuario: ").strip()
    
    if not validate_username(user) or user in accounts:
        print("Nombre inválido o ya existe.")
        wait()
        return
    
    pwd = input("Contraseña: ").strip()
    if not pwd:
        print("La contraseña no puede quedar vacía.")
        wait()
        return
    elif len(pwd) > 50:
        print("Contraseña demasiado larga, debe de tener menos de 50 caracteres.")
        wait()
        return
    
    amount = parse_integer_amount(input("Depósito inicial: ").strip())
    if amount is None or amount < 0:
        print("Depósito inválido. Solo se aceptan numeros enteros.")
        wait()
        return
    
    pin = input("Crea tu PIN (solo numeros): ").strip()
    if not pin.isdigit() or len(pin) < 4:
        print("PIN invalido. Debe de tener 4 digitos, su pin debe ser numerico")
        wait()
        return
    
    if pwd == pin:
        print("El PIN no puede ser igual a la contraseña.")
        wait()
        return
    
    pwd_hash, pwd_salt = hash_password(pwd)
    pin_hash, pin_salt = hash_password(pin)
    
    accounts[user] = {
        "user": user,
        "pwd": pwd_hash,
        "pwd_salt": pwd_salt,
        "pin": pin_hash,
        "pin_salt": pin_salt,
        "balance": amount,
        "history": [],
        "bloqueado": False,
        "intentos_fallidos": 0,
        "fecha_intentos": "",
        "ultimo_acceso": "",
        "retiro_hoy": 0,
        "transferencia_hoy": 0,
        "fecha_limite": "",
    }
    
    record(accounts[user], "Depósito inicial", amount)
    save_data(accounts)
    save_user_file(accounts[user])
    print("Cuenta creada con éxito.")
    wait()

def change_password(acc, accounts: dict):
    header("Cambiar contraseña")
    pwd_actual = input("Contraseña actual: ").strip()
    
    if not verify_password(pwd_actual, acc["pwd"], acc["pwd_salt"]):
        print(f"{RED}Contraseña incorrecta.{RESET}")
        wait()
        return
    
    pwd_nueva = input("Nueva contraseña: ").strip()
    if not pwd_nueva:
        print(f"{RED}La contraseña no puede quedar vacía.{RESET}")
        wait()
        return
    
    if len(pwd_nueva) > 50:
        print(f"{RED}Contraseña demasiado larga, maximo de 50 caracteres.{RESET}")
        wait()
        return
    
    if pwd_nueva == pwd_actual:
        print(f"{RED}La nueva contraseña no puede ser igual a la actual.{RESET}")
        wait()
        return
    
    pwd_hash, pwd_salt = hash_password(pwd_nueva)
    acc["pwd"] = pwd_hash
    acc["pwd_salt"] = pwd_salt
    save_data(accounts)
    print(f"{GREEN}Contraseña cambiada con éxito.{RESET}")
    wait()

def change_pin(acc, accounts: dict, pin_attempts: dict):
    header("Cambiar PIN")
    pin_actual = input("PIN actual: ").strip()
    
    if not verify_password(pin_actual, acc["pin"], acc["pin_salt"]):
        print(f"{RED}PIN incorrecto.{RESET}")
        wait()
        return
    
    pin_nuevo = input("Nuevo PIN (solo numeros, 4 digitos): ").strip()
    if not pin_nuevo.isdigit() or len(pin_nuevo) < 4:
        print(f"{RED}PIN invalido. Debe de tener 4 digitos, su pin debe ser numerico.{RESET}")
        wait()
        return
    
    if pin_nuevo == pin_actual:
        print(f"{RED}El nuevo PIN debe ser diferente al actual.{RESET}")
        wait()
        return
    
    pin_confirm = input("Confirma el nuevo PIN: ").strip()
    if pin_nuevo != pin_confirm:
        print(f"{RED}Los PIN's no coinciden.{RESET}")
        wait()
        return
    
    if verify_password(pin_nuevo, acc["pwd"], acc["pwd_salt"]):
        print(f"{RED}El PIN no puede ser igual a la contraseña.{RESET}")
        wait()
        return
    
    pin_hash, pin_salt = hash_password(pin_nuevo)
    acc["pin"] = pin_hash
    acc["pin_salt"] = pin_salt
    save_data(accounts)
    pin_attempts[acc["user"]] = 0
    print(f"{GREEN}PIN cambiado con exito.{RESET}")
    wait()