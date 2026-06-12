import os
import re
from config import (
    BOLD, RESET, CYAN, GREEN, YELLOW, MAGENTA, RED, 
    BANK_NAME, CURRENCY_SYMBOL)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def wait(msg="Presiona Enter para continuar..."):
    input(msg)

def header(title):
    clear()
    print(f"{BOLD}{CYAN}=== Bienvenido a la banca {BANK_NAME} ==={RESET}")
    print(f"{MAGENTA}--- {title} ---{RESET}\n")

def print_ticket(acc, kind, amount, target=None):
    print(f"\n{BOLD}{MAGENTA}=== COMPROBANTE DE {kind.upper()} ==={RESET}")
    print(f"{YELLOW}Usuario: {acc['user']}{RESET}")
    if target:
        print(f"{YELLOW}Destino: {target}{RESET}")
        print(f"{GREEN}Monto: {CURRENCY_SYMBOL} {amount:.2f}{RESET}")
        print(f"{GREEN}Saldo actual: {CURRENCY_SYMBOL} {acc['balance']:.2f}{RESET}")
        print(f"{MAGENTA}{'-'*32}{RESET}")

def confirmar_operacion(detalle: str) -> bool:
    print(f"\n{BOLD}{YELLOW}=== CONFIRMAR OPERACION ==={RESET}")
    print(detalle)
    print(f"{YELLOW}{'='*30}{RESET}")
    resp = input(f"{BOLD}¿Confirmar? (S/N): {RESET}").strip().upper()
    return resp == "S"

def parse_integer_amount(value):
    try:
        num_str = value.replace(",", ".").strip()
        num = float(num_str)
        if num != int(num):
            return None
        return int(num)
    except Exception:
        return None

def validate_username(user: str) -> bool:
    if not user or len(user) > 30:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', user))

def print_account_info(acc):
    print(f"{CYAN}Usuario     : {acc['user']}{RESET}")
    print(f"{GREEN}Saldo       : {CURRENCY_SYMBOL} {acc['balance']:.2f}{RESET}")
    print(f"{YELLOW}Movimientos : {len(acc['history'])}{RESET}")

def print_history_table(acc):
    if not acc["history"]:
        print("No hay movimientos registrados.")
    else:
        print(f"{'Fecha':<19} | {'Tipo':<24} | {'Monto':>10} | {'Saldo':>10}")
        print("-" * 67)
        for m in acc["history"]:
            sign = "+" if m["amount"] >= 0 else ""
            print(f"{m['date']:<19} | {m['type']:<24} | {sign}{m['amount']:>9.2f} | {CURRENCY_SYMBOL} {m['balance']:>8.2f}")