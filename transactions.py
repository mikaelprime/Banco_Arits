import time
from config import CYAN, GREEN, YELLOW, RED, MAGENTA, RESET, CURRENCY_SYMBOL
from security import verify_password
from display import header, wait, parse_integer_amount, print_ticket, confirmar_operacion
from data import record, save_data, save_user_file

def verify_pin(acc, pin_attempts: dict):
    from security import log_sospechoso
    
    user = acc["user"]
    while True:
        intentos = pin_attempts.get(user, 0)
        if intentos >= 3:
            print(f"{RED}Demasiados intentos fallidos. Favor espere 20 segundos.{RESET}")
            time.sleep(20)
            pin_attempts[user] = 0

        pin = input("Ingresa tu PIN: ").strip()
        if verify_password(pin, acc["pin"], acc["pin_salt"]):
            pin_attempts[user] = 0
            return True

        pin_attempts[user] = pin_attempts.get(user, 0) + 1
        log_sospechoso("Intentos fallidos de PIN", user)
        restantes = 3 - pin_attempts[user]

        if restantes > 0:
            print(f"{YELLOW}PIN incorrecto. Intentos restantes: {restantes}{RESET}")
        else:
            print(f"{RED}Demasiados intentos fallidos. Bloqueado por 20 segundos.{RESET}")

def show_balance(acc):
    header("Saldo de la cuenta")
    print(f"Saldo actual: {CURRENCY_SYMBOL} {acc['balance']:.2f}")
    wait()

def deposit(acc, accounts: dict, pin_attempts: dict):
    header("Depósito")
    if not verify_pin(acc, pin_attempts):
        wait()
        return
    
    amount = parse_integer_amount(input("Monto a depositar: ").strip())
    if amount is None or amount <= 0:
        print("Monto invalido. Solo se aceptan numeros enteros.")
        wait()
        return
    
    detalle = (
        f"{CYAN}Operacion      : Depósito{RESET}"
        f"{GREEN}Monto         : {CURRENCY_SYMBOL} {amount:.2f}{RESET}\n"
        f"{GREEN}Saldo actual  : {CURRENCY_SYMBOL} {acc['balance']:.2f}{RESET}\n"
        f"{GREEN}Saldo después : {CURRENCY_SYMBOL} {acc['balance'] + amount:.2f}{RESET}"
    )
    
    if not confirmar_operacion(detalle):
        print(f"{YELLOW}Operacion cancelada.{RESET}")
        wait()
        return
    
    acc["balance"] += amount
    record(acc, "Deposito", amount)
    save_data(accounts)
    save_user_file(acc)
    print_ticket(acc, "Deposito", amount)
    wait()

def withdraw(acc, accounts: dict, pin_attempts: dict):
    header("Retiro")
    if not verify_pin(acc, pin_attempts):
        wait()
        return
    
    amount = parse_integer_amount(input("Monto a retirar: ").strip())
    if amount is None or amount <= 0 or amount > acc["balance"]:
        print("Monto invalido o saldo insuficiente. Solo se aceptan numeros enteros.")
        wait()
        return
    
    detalle = (
        f"{CYAN}Operacion       : Retiro{RESET}\n"
        f"{YELLOW}Monto         : {CURRENCY_SYMBOL} {amount:.2f}{RESET}\n"
        f"{GREEN}Saldo actual   : {CURRENCY_SYMBOL} {acc['balance']:.2f}{RESET}\n"
        f"{YELLOW}Saldo después : {CURRENCY_SYMBOL} {acc['balance'] - amount:.2f}{RESET}"
    )
    
    if not confirmar_operacion(detalle):
        print(f"{YELLOW}Operacion cancelada.{RESET}")
        wait()
        return
    
    acc["balance"] -= amount
    record(acc, "Retiro", -amount)
    save_data(accounts)
    save_user_file(acc)
    print_ticket(acc, "Retiro", amount)
    wait()

def transfer(user, accounts: dict, pin_attempts: dict):
    header("Transferencia")
    origin = accounts.get(user)
    
    if not verify_pin(origin, pin_attempts):
        wait()
        return
    
    target = input("Cuenta destino: ").strip()
    if target == user or target not in accounts:
        print("Cuenta destino inválida.")
        wait()
        return
    
    amount = parse_integer_amount(input("Monto a transferir: ").strip())
    if amount is None or amount <= 0 or amount > origin["balance"]:
        print("Monto invalido o saldo insuficiente. Solo se aceptan numeros enteros.")
        wait()
        return
    
    detalle = (
        f"{CYAN}Operacion       : Transferencia{RESET}\n"
        f"{MAGENTA}Destino      : {target}{RESET}\n"
        f"{YELLOW}Monto         : {CURRENCY_SYMBOL} {amount:.2f}{RESET}\n"
        f"{GREEN}Saldo actual   : {CURRENCY_SYMBOL} {origin['balance']:.2f}{RESET}\n"
        f"{YELLOW}Saldo después : {CURRENCY_SYMBOL} {origin['balance'] - amount:.2f}{RESET}"
    )
    
    if not confirmar_operacion(detalle):
        print(f"{YELLOW}Operacion cancelada.{RESET}")
        wait()
        return
    
    dest = accounts[target]
    origin["balance"] -= amount
    dest["balance"] += amount
    record(origin, "Transferencia enviada", -amount)
    record(dest, "Transferencia recibida", amount)
    save_data(accounts)
    save_user_file(origin)
    save_user_file(dest)
    print_ticket(origin, "Transferencia", amount, target=target)
    wait()

def show_history(acc):
    from display import print_history_table
    
    header("Historial de movimientos")
    print_history_table(acc)
    wait()