import os
import json
from datetime import datetime
from config import DATA_FILE, ACCOUNTS_DIR, CURRENCY_SYMBOL, BANK_NAME

def save_user_file(acc):
    user = acc["user"]
    path = os.path.join(ACCOUNTS_DIR, f"{user}.json")

    resumen = {
        "=== ESTADO DE CUENTA ===": f"Banco {BANK_NAME}",
        "usuario": user,
        "saldo_actual": f"{CURRENCY_SYMBOL} {acc['balance']:.2f}",
        "total_movimientos": len(acc["history"]),
        "ultima_operacion": acc["history"][-1]["date"] if acc["history"] else "Sin movimientos",
        "historial": [
            {
                "fecha": m["date"],
                "tipo": m["type"],
                "monto": f"{'+' if m['amount'] >= 0 else ''}{m['amount']:.2f}",
                "saldo_despues": f"{CURRENCY_SYMBOL} {m['balance']:.2f}",
            }
            for m in acc["history"]
        ],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)

def save_data(accounts: dict):
    sorted_accounts = dict(sorted(accounts.items()))
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_accounts, f, indent=2, ensure_ascii=False)

    for acc in accounts.values():
        save_user_file(acc)

def load_data() -> dict:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def initialize_accounts_dir():
    os.makedirs(ACCOUNTS_DIR, exist_ok=True)

def record(acc, kind, amount):
    acc["history"].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": kind,
        "amount": amount,
        "balance": acc["balance"],
    })

def get_monto_usado_hoy(acc, tipo: str) -> int:
    hoy = datetime.now().strftime("%Y-%m-%d")
    total = 0
    for m in acc["history"]:
        if m["date"].startswith(hoy) and m["type"] == tipo:
            total += abs(m["amount"])
    return total

def guardar_solicitud(usuario: str, motivo: str, explicacion: str):
    import json
    SOLICITUDES_DIR = "solicitudes"
    os.makedirs(SOLICITUDES_DIR, exist_ok=True)

    path = os.path.join(SOLICITUDES_DIR, f"{usuario}_Solicitud.json")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"usuario": usuario, "solicitudes": []}

    data["solicitudes"].append({
        "fecha":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "motivo":      motivo,
        "explicacion": explicacion,
        "estado":      "pendiente",
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)