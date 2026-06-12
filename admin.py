import time
from config import CYAN, GREEN, YELLOW, MAGENTA, RED, RESET, CURRENCY_SYMBOL, LOG_FILE, BOLD
from security import hash_password, verify_password, log_sospechoso
from display import header, wait, print_history_table
from data import save_data

def view_all_accounts(accounts: dict):
    header("Todas las cuentas")
    if not accounts:
        print("No hay cuentas registradas.")
    else:
        for user, acc in sorted(accounts.items()):
            estado = f"{RED}BLOQUEADA{RESET}" if acc.get("bloqueado") else f"{GREEN}ACTIVA{RESET}"
            print(f"{CYAN}Usuario     : {acc['user']}{RESET}")
            print(f"{GREEN}Saldo       : {CURRENCY_SYMBOL} {acc['balance']:.2f}{RESET}")
            print(f"{YELLOW}Movimientos : {len(acc['history'])}{RESET}")
            print(f"Estado      : {estado}")
            print(f"{MAGENTA}{'-' * 30}{RESET}")
    wait()

def reactivate_account(accounts: dict):
    header("Reactivar cuenta bloqueada")
    bloqueadas = [u for u, a in accounts.items() if a.get("bloqueado")]
    
    if not bloqueadas:
        print(f"{GREEN}No hay cuentas bloqueadas.{RESET}")
        wait()
        return
    
    print(f"{YELLOW}Cuentas bloqueadas:{RESET}\n")
    for u in sorted(bloqueadas):
        print(f"  {RED}→ {u}{RESET}")
    print()
    
    user = input("Nombre de usuario a reactivar: ").strip()
    if user not in bloqueadas:
        print(f"{RED}Esa cuenta no está bloqueada o no existe.{RESET}")
        wait()
        return
    
    accounts[user]["bloqueado"] = False
    accounts[user]["intentos_fallidos"] = 0
    accounts[user]["fecha_intentos"] = ""
    save_data(accounts)
    print(f"{GREEN}Cuenta '{user}' reactivada con éxito.{RESET}")
    wait()

def view_security_log():
    header("Log de seguridad")
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        if not lineas:
            print("No hay actividad sospechosa registrada.")
        else:
            print(f"{YELLOW}{'='*67}{RESET}")
            for linea in lineas[-50:]: 
                print(f"{RED}{linea.strip()}{RESET}")
            print(f"{YELLOW}{'='*67}{RESET}")
    except FileNotFoundError:
        print("No hay actividad sospechosa registrada.")
    wait()

def reset_user_password(accounts: dict):
    header("Resetear contraseña de usuario")
    user = input("Nombre de usuario: ").strip()
    
    if user not in accounts:
        print(f"{RED}Usuario no encontrado.{RESET}")
        wait()
        return
    
    pwd_nueva = input("Nueva contraseña temporal: ").strip()
    if not pwd_nueva or len(pwd_nueva) > 50:
        print(f"{RED}Contraseña inválida.{RESET}")
        wait()
        return
    
    pwd_hash, pwd_salt = hash_password(pwd_nueva)
    accounts[user]["pwd"] = pwd_hash
    accounts[user]["pwd_salt"] = pwd_salt
    save_data(accounts)
    log_sospechoso(f"Admin reseteó contraseña", user)
    print(f"{GREEN}Contraseña de '{user}' reseteada con éxito.{RESET}")
    wait()

def reset_user_pin(accounts: dict):
    header("Resetear PIN de usuario")
    user = input("Nombre de usuario: ").strip()
    
    if user not in accounts:
        print(f"{RED}Usuario no encontrado.{RESET}")
        wait()
        return
    
    pin_nuevo = input("Nuevo PIN temporal (4-8 dígitos): ").strip()
    if not pin_nuevo.isdigit() or len(pin_nuevo) < 4 or len(pin_nuevo) > 8:
        print(f"{RED}PIN inválido.{RESET}")
        wait()
        return
    
    pin_hash, pin_salt = hash_password(pin_nuevo)
    accounts[user]["pin"] = pin_hash
    accounts[user]["pin_salt"] = pin_salt
    save_data(accounts)
    log_sospechoso(f"Admin reseteó PIN", user)
    print(f"{GREEN}PIN de '{user}' reseteado con éxito.{RESET}")
    wait()

def view_user_history(accounts: dict):
    header("Historial de usuario")
    
    if not accounts:
        print(f"{RED}No hay cuentas registradas.{RESET}")
        wait()
        return
    
    print(f"{YELLOW}Usuarios registrados:{RESET}\n")
    for u in sorted(accounts.keys()):
        estado = f"{RED}BLOQUEADA{RESET}" if accounts[u].get("bloqueado") else f"{GREEN}ACTIVA{RESET}"
        print(f"  → {CYAN}{u}{RESET} [{estado}]")
    print()
    
    user = input("Nombre de usuario a consultar: ").strip()
    if user not in accounts:
        print(f"{RED}Usuario no encontrado.{RESET}")
        wait()
        return
    
    acc = accounts[user]
    header(f"Historial de {user}")
    print(f"{CYAN}Usuario : {user}{RESET}")
    print(f"{GREEN}Saldo actual : {CURRENCY_SYMBOL} {acc['balance']:.2f}{RESET}")
    print(f"{YELLOW}Total movimientos : {len(acc['history'])}{RESET}")
    print(f"{YELLOW}Último acceso : {acc.get('ultimo_acceso', 'Sin registros')}{RESET}\n")
    print(f"{CYAN}{'Fecha':<19} | {'Tipo':<24} | {'Monto':>10} | {'Saldo':>10}{RESET}")
    print("-" * 67)
    print_history_table(acc)
    wait()

def admin_panel(accounts: dict):
    while True:
        header("Panel de Administrador")
        print(f"{BOLD}{RED}=== PANEL DE ADMINISTRADOR ==={RESET}\n")
        print(f"{GREEN}1. Ver todas las cuentas{RESET}")
        print(f"{CYAN}2. Reactivar cuenta bloqueada{RESET}")
        print(f"{YELLOW}3. Ver log de seguridad{RESET}")
        print(f"{MAGENTA}4. Resetear contraseña de usuario{RESET}")
        print(f"{MAGENTA}5. Resetear PIN de usuario{RESET}")
        print(f"{GREEN}6. Ver historial de un usuario{RESET}")
        print(f"{RED}7. Salir del panel{RESET}\n")
        
        choice = input(f"{GREEN}Selecciona una opción: {RESET}").strip()

        if choice == "1":
            view_all_accounts(accounts)
        elif choice == "2":
            reactivate_account(accounts)
        elif choice == "3":
            view_security_log()
        elif choice == "4":
            reset_user_password(accounts)
        elif choice == "5":
            reset_user_pin(accounts)
        elif choice == "6":
            view_user_history(accounts)
        elif choice == "7":
            break
        else:
            print("Opción inválida.")
            wait()