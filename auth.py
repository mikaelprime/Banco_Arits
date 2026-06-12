import time
from datetime import datetime
from config import YELLOW, RED, CYAN, GREEN, BOLD, RESET
from security import verify_password, log_sospechoso
from display import header, wait

def login(accounts: dict, login_attempts: dict) -> str:
    header("Iniciar sesión")
    user = input("Nombre de usuario: ").strip()
    acc = accounts.get(user)
    
    if not acc:
        print(f"{RED}Usuario o contraseña incorrecta.{RESET}")
        wait()
        return None
        
    if acc.get("bloqueado"):
        print(f"{RED}Esta cuenta esta bloqueada. Favor contactar con el administrador.{RESET}")
        wait()
        return None

    while True:
        intentos_temp = login_attempts.get(user, 0)
        if intentos_temp >= 3:
            print(f"{RED}Cuenta bloqueada temporalmente. Espera 20 segundos.{RESET}")
            time.sleep(20)
            login_attempts[user] = 0

        pwd = input("Contraseña: ").strip()

        if verify_password(pwd, acc["pwd"], acc["pwd_salt"]):
            login_attempts[user] = 0
            acc["intentos_fallidos"] = 0
            acc["fecha_intentos"] = ""
            ultimo = acc.get("ultimo_acceso", "")
            acc["ultimo_acceso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n{BOLD}{GREEN}¡Bienvenido, {user}!{RESET}")
            if ultimo:
                print(f"{CYAN}Ultimo acceso: {ultimo}{RESET}")
            else:
                print(f"{CYAN}Primer inicio de sesion.{RESET}")
            time.sleep(2)
            return user

        login_attempts[user] = login_attempts.get(user, 0) + 1
        hoy = datetime.now().strftime("%Y-%m-%d")

        if  acc.get("fecha_intentos") != hoy:
            acc["intentos_fallidos"] = 0
            acc["fecha_intentos"] = hoy

        acc["intentos_fallidos"] += 1
        log_sospechoso("Intento fallido de login", user)
        restantes_temp = 3 - login_attempts[user]

        if acc["intentos_fallidos"] >= 5:
            acc["bloqueado"] = True
            log_sospechoso("Cuenta bloqueada por exceso de intentos fallidos", user)
            print(f"{RED}Demasiados intentos fallidos hoy. Cuenta bloqueada permanentemente.{RESET}")
            print(f"{RED}Contacta al administrador para reactivarla.{RESET}")
            wait()
            return None

        if restantes_temp > 0:
            print(f"{YELLOW}Contraseña incorrecta. Intentos restantes: {restantes_temp}{RESET}")
        else:
            print(f"{RED}Demasiados intentos seguidos. Bloqueado 20 segundos.{RESET}")