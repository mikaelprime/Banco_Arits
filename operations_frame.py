import tkinter as tk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (BG_MAIN, BG_CARD, ACCENT, FONT_SUBTITLE, TEXT_PRIMARY, TEXT_SECONDARY,
                    FONT_TITLE, FONT_NORMAL, FONT_BTN, FONT_SMALL,
                    TEXT_ERROR, TEXT_SUCCESS, TEXT_WARNING, CURRENCY_SYMBOL,
                    ACCENT_HOVER, BG_SECONDARY)
from security import verify_password, hash_password, log_sospechoso
from data import save_data, save_user_file, record

def make_entry(parent, show=None):
    e = tk.Entry(parent, font=FONT_NORMAL, bg="#1a1a2e", fg=TEXT_PRIMARY,
                insertbackground=TEXT_PRIMARY, relief="flat",
                highlightthickness=1, highlightbackground=ACCENT,
                highlightcolor=ACCENT)
    if show:
        e.config(show="●")
    return e

class PinVerifyWidget(tk.Frame):

    def __init__(self, parent, app, on_success):
        super().__init__(parent, bg=BG_CARD)
        self.app        = app
        self.on_success = on_success
        self.acc        = app.accounts.get(app.current_user)
        self._build()

    def _build(self):
        tk.Label(self, text="🔐 Verificación de PIN",
                font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_SECONDARY).pack(pady=(10, 5))

        self.pin_entry = make_entry(self, show=True)
        self.pin_entry.pack(fill="x", padx=20, pady=(0, 8))
        self.pin_entry.bind("<Return>", lambda e: self._verify())

        tk.Button(self, text="Confirmar PIN", command=self._verify,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=6,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_PRIMARY
                ).pack(fill="x", padx=20, pady=(0, 8))

        self.msg = tk.Label(self, text="", font=FONT_SMALL,
                            bg=BG_CARD, fg=TEXT_ERROR)
        self.msg.pack()

    def _verify(self):
        pin  = self.pin_entry.get().strip()
        user = self.app.current_user
        intentos = self.app.pin_attempts.get(user, 0)

        if intentos >= 3:
            self.msg.config(
                text="PIN bloqueado 20 seg.", fg=TEXT_ERROR)
            self.app.after(20000, lambda: self._reset_pin(user))
            return

        if verify_password(pin, self.acc["pin"], self.acc["pin_salt"]):
            self.app.pin_attempts[user] = 0
            self.on_success()
        else:
            self.app.pin_attempts[user] = intentos + 1
            log_sospechoso("Intento fallido de PIN", user)
            restantes = 3 - self.app.pin_attempts[user]
            if restantes > 0:
                self.msg.config(
                    text=f"PIN incorrecto. Intentos restantes: {restantes}",
                    fg=TEXT_ERROR)
            else:
                self.msg.config(
                    text="Demasiados intentos. Bloqueado 20 seg.",
                    fg=TEXT_ERROR)
            self.pin_entry.delete(0, "end")

    def _reset_pin(self, user):
        self.app.pin_attempts[user] = 0
        self.msg.config(text="Ya puedes intentar de nuevo.", fg=TEXT_SUCCESS)

class OperationFrame(tk.Frame):
    CONFIGS = {
        "deposit": {
            "title": "Depósito",
            "icon":  "💰",
            "label": "Monto a depositar",
            "color": TEXT_SUCCESS,
        },
        "withdraw": {
            "title": "Retiro",
            "icon":  "💸",
            "label": "Monto a retirar",
            "color": TEXT_WARNING,
        },
        "transfer": {
            "title": "Transferencia",
            "icon":  "🔁",
            "label": "Monto a transferir",
            "color": ACCENT,
        },
    }

    def __init__(self, parent, app, operation):
        super().__init__(parent, bg=BG_MAIN)
        self.app       = app
        self.operation = operation
        self.acc       = app.accounts.get(app.current_user)
        self.cfg       = self.CONFIGS[operation]
        self.pin_ok    = False
        self._build()

    def _build(self):
        tk.Label(self, text=f"{self.cfg['icon']}  {self.cfg['title']}",
                font=FONT_TITLE, bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(25, 5))
        tk.Label(self,
                text=f"Saldo actual: {CURRENCY_SYMBOL} {self.acc['balance']:.2f}",
                font=FONT_NORMAL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(pady=(0, 15))

        self.card = tk.Frame(self, bg=BG_CARD, padx=30, pady=25)
        self.card.pack(padx=40, fill="x")

        self.pin_widget = PinVerifyWidget(self.card, self.app, self._on_pin_ok)
        self.pin_widget.pack(fill="x", pady=(0, 15))

        tk.Frame(self.card, bg=ACCENT, height=1).pack(fill="x", pady=10)

        self.fields_frame = tk.Frame(self.card, bg=BG_CARD)
        self.fields_frame.pack(fill="x")

        if self.operation == "transfer":
            tk.Label(self.fields_frame, text="Cuenta destino",
                    font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")
            self.target_entry = make_entry(self.fields_frame)
            self.target_entry.pack(fill="x", pady=(3, 12))
            self.target_entry.config(state="disabled")

        tk.Label(self.fields_frame, text=self.cfg["label"],
                font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")
        self.amount_entry = make_entry(self.fields_frame)
        self.amount_entry.pack(fill="x", pady=(3, 15))
        self.amount_entry.config(state="disabled")

        self.msg = tk.Label(self.fields_frame, text="",
                            font=FONT_SMALL, bg=BG_CARD,
                            fg=TEXT_ERROR, wraplength=380)
        self.msg.pack(pady=(0, 8))

        self.exec_btn = tk.Button(
            self.fields_frame, text=f"Confirmar {self.cfg['title']}",
            command=self._execute,
            font=FONT_BTN, bg=self.cfg["color"], fg=TEXT_PRIMARY,
            relief="flat", cursor="hand2", pady=10,
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_PRIMARY, state="disabled"
        )
        self.exec_btn.pack(fill="x", pady=(0, 10))

        tk.Button(self.card, text="← Volver",
                command=self.app.show_account_menu,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2",
                activebackground=BG_CARD,
                activeforeground=TEXT_PRIMARY
                ).pack()

    def _on_pin_ok(self):
        self.pin_widget.msg.config(text="✓ PIN verificado", fg=TEXT_SUCCESS)
        self.pin_widget.pin_entry.config(state="disabled")
        self.amount_entry.config(state="normal")
        self.exec_btn.config(state="normal")
        if self.operation == "transfer":
            self.target_entry.config(state="normal")
        self.amount_entry.focus()

    def _parse_amount(self, value):
        try:
            num = float(value.replace(",", ".").strip())
            if num != int(num) or int(num) <= 0:
                return None
            return int(num)
        except Exception:
            return None

    def _execute(self):
        amount = self._parse_amount(self.amount_entry.get())
        if amount is None:
            self.msg.config(
                text="Monto invalido. Solo números enteros positivos.",
                fg=TEXT_ERROR)
            return

        if self.operation == "deposit":
            self._do_deposit(amount)
        elif self.operation == "withdraw":
            self._do_withdraw(amount)
        elif self.operation == "transfer":
            self._do_transfer(amount)

    def _do_deposit(self, amount):
        self.acc["balance"] += amount
        record(self.acc, "Depósito", amount)
        save_data(self.app.accounts)
        save_user_file(self.acc)
        self._show_ticket("Depósito", amount)

    def _do_withdraw(self, amount):
        from config import LIMITE_RETIRO_DIARIO
        from datetime import datetime
        hoy = datetime.now().strftime("%Y-%m-%d")

        if self.acc.get("fecha_limite") != hoy:
            self.acc["retiro_hoy"]        = 0
            self.acc["transferencia_hoy"] = 0
            self.acc["fecha_limite"]      = hoy

        usado = self.acc.get("retiro_hoy", 0)
        if usado + amount > LIMITE_RETIRO_DIARIO:
            restante = LIMITE_RETIRO_DIARIO - usado
            self.msg.config(
                text=f"Límite diario de retiro alcanzado.\n"
                    f"Disponible hoy: $ {restante:.2f} de $ {LIMITE_RETIRO_DIARIO:.2f}",
                fg=TEXT_ERROR)
            return
        
        if amount > self.acc["balance"]:
            self.msg.config(text="Saldo insuficiente.", fg=TEXT_ERROR)
            return
        
        self.acc["retiro_hoy"] = usado + amount
        self.acc["balance"] -= amount
        record(self.acc, "Retiro", -amount)
        save_data(self.app.accounts)
        save_user_file(self.acc)
        self._show_ticket("Retiro", amount)

    def _do_transfer(self, amount):
        target = self.target_entry.get().strip()
        user   = self.app.current_user
        if not target or target == user or target not in self.app.accounts:
            self.msg.config(text="Cuenta destino invalida.", fg=TEXT_ERROR)
            return
        from config import LIMITE_TRANSFERENCIA_DIARIA
        from datetime import datetime
        hoy = datetime.now().strftime("%Y-%m-%d")

        if self.acc.get("fecha_limite") != hoy:
            self.acc["retiro_hoy"]        = 0
            self.acc["transferencia_hoy"] = 0
            self.acc["fecha_limite"]      = hoy

        usado = self.acc.get("transferencia_hoy", 0)
        if usado + amount > LIMITE_TRANSFERENCIA_DIARIA:
            restante = LIMITE_TRANSFERENCIA_DIARIA - usado
            self.msg.config(
                text=f"Límite diario de transferencia alcanzado.\n"
                    f"Disponible hoy: $ {restante:.2f} de $ {LIMITE_TRANSFERENCIA_DIARIA:.2f}",
                fg=TEXT_ERROR)
            return

        if amount > self.acc["balance"]:
            self.msg.config(text="Saldo insuficiente.", fg=TEXT_ERROR)
            return

        self.acc["transferencia_hoy"] = usado + amount
        dest = self.app.accounts[target]
        self.acc["balance"]  -= amount
        dest["balance"]      += amount
        record(self.acc, "Transferencia enviada",   -amount)
        record(dest,     "Transferencia recibida",   amount)
        save_data(self.app.accounts)
        save_user_file(self.acc)
        save_user_file(dest)
        self._show_ticket("Transferencia", amount, target=target)

    def _show_ticket(self, kind, amount, target=None):
        win = tk.Toplevel(self.app)
        win.title("Comprobante")
        win.geometry("360x300")
        win.configure(bg=BG_SECONDARY)
        win.resizable(False, False)

        tk.Label(win, text="✅ Operación exitosa",
                font=FONT_SUBTITLE, bg=BG_SECONDARY, fg=TEXT_SUCCESS).pack(pady=(20, 5))
        tk.Label(win, text=f"=== COMPROBANTE DE {kind.upper()} ===",
                font=FONT_NORMAL, bg=BG_SECONDARY, fg=ACCENT).pack()

        tk.Frame(win, bg=ACCENT, height=1).pack(fill="x", padx=30, pady=10)

        info = tk.Frame(win, bg=BG_SECONDARY)
        info.pack(padx=30, fill="x")

        rows = [
            ("Usuario",       self.app.current_user),
            ("Tipo",          kind),
            ("Monto",         f"{CURRENCY_SYMBOL} {amount:.2f}"),
            ("Saldo actual",  f"{CURRENCY_SYMBOL} {self.acc['balance']:.2f}"),
        ]
        if target:
            rows.insert(2, ("Destino", target))

        for label, value in rows:
            row = tk.Frame(info, bg=BG_SECONDARY)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{label}:", font=FONT_SMALL,
                    bg=BG_SECONDARY, fg=TEXT_SECONDARY, width=14,
                    anchor="w").pack(side="left")
            tk.Label(row, text=value, font=FONT_NORMAL,
                    bg=BG_SECONDARY, fg=TEXT_PRIMARY).pack(side="left")

        tk.Button(win, text="Cerrar",
                command=lambda: [win.destroy(), self.app.show_account_menu()],
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=8
                ).pack(pady=15)

class ChangePasswordFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_MAIN)
        self.app = app
        self.acc = app.accounts.get(app.current_user)
        self._build()

    def _build(self):
        tk.Label(self, text="🔑  Cambiar Contraseña",
                font=FONT_TITLE, bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(30, 20))

        card = tk.Frame(self, bg=BG_CARD, padx=30, pady=25)
        card.pack(padx=40, fill="x")

        campos = [
            ("Contraseña actual",  "pwd_actual"),
            ("Nueva contraseña",   "pwd_nueva"),
            ("Confirmar nueva",    "pwd_confirm"),
        ]
        self.entries = {}
        for label, key in campos:
            tk.Label(card, text=label, font=FONT_NORMAL,
                    bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")
            e = make_entry(card, show=True)
            e.pack(fill="x", pady=(3, 12))
            self.entries[key] = e

        self.msg = tk.Label(card, text="", font=FONT_SMALL,
                            bg=BG_CARD, fg=TEXT_ERROR, wraplength=380)
        self.msg.pack(pady=(0, 8))

        tk.Button(card, text="Cambiar Contraseña", command=self._change,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=10,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_PRIMARY
                ).pack(fill="x", pady=(0, 10))

        tk.Button(card, text="← Volver",
                command=self.app.show_account_menu,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2"
                ).pack()

    def _change(self):
        actual  = self.entries["pwd_actual"].get().strip()
        nueva   = self.entries["pwd_nueva"].get().strip()
        confirm = self.entries["pwd_confirm"].get().strip()

        if not verify_password(actual, self.acc["pwd"], self.acc["pwd_salt"]):
            self.msg.config(text="Contraseña actual incorrecta.", fg=TEXT_ERROR); return
        if not nueva or len(nueva) > 50:
            self.msg.config(text="Contraseña invalida.", fg=TEXT_ERROR); return
        if nueva == actual:
            self.msg.config(text="Debe ser diferente a la actual.", fg=TEXT_ERROR); return
        if nueva != confirm:
            self.msg.config(text="Las contraseñas no coinciden.", fg=TEXT_ERROR); return

        self.acc["pwd"], self.acc["pwd_salt"] = hash_password(nueva)
        save_data(self.app.accounts)
        self.msg.config(text="✓ Contraseña cambiada con exito.", fg=TEXT_SUCCESS)
        self.app.after(1500, self.app.show_account_menu)

class ChangePinFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_MAIN)
        self.app = app
        self.acc = app.accounts.get(app.current_user)
        self._build()

    def _build(self):
        tk.Label(self, text="🔐  Cambiar PIN",
                font=FONT_TITLE, bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(30, 20))

        card = tk.Frame(self, bg=BG_CARD, padx=30, pady=25)
        card.pack(padx=40, fill="x")

        campos = [
            ("PIN actual",       "pin_actual"),
            ("Nuevo PIN",        "pin_nuevo"),
            ("Confirmar PIN",    "pin_confirm"),
        ]
        self.entries = {}
        for label, key in campos:
            tk.Label(card, text=label, font=FONT_NORMAL,
                    bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")
            e = make_entry(card, show=True)
            e.pack(fill="x", pady=(3, 12))
            self.entries[key] = e

        self.msg = tk.Label(card, text="", font=FONT_SMALL,
                            bg=BG_CARD, fg=TEXT_ERROR, wraplength=380)
        self.msg.pack(pady=(0, 8))

        tk.Button(card, text="Cambiar PIN", command=self._change,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=10,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_PRIMARY
                ).pack(fill="x", pady=(0, 10))

        tk.Button(card, text="← Volver",
                command=self.app.show_account_menu,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2"
                ).pack()

    def _change(self):
        actual  = self.entries["pin_actual"].get().strip()
        nuevo   = self.entries["pin_nuevo"].get().strip()
        confirm = self.entries["pin_confirm"].get().strip()

        if not verify_password(actual, self.acc["pin"], self.acc["pin_salt"]):
            self.msg.config(text="PIN actual incorrecto.", fg=TEXT_ERROR); return
        if not nuevo.isdigit() or len(nuevo) != 4:
            self.msg.config(text="PIN invalido. 4 digitos numericos.", fg=TEXT_ERROR); return
        if nuevo == actual:
            self.msg.config(text="Debe ser diferente al actual.", fg=TEXT_ERROR); return
        if nuevo != confirm:
            self.msg.config(text="Los PINs no coinciden.", fg=TEXT_ERROR); return
        if verify_password(nuevo, self.acc["pwd"], self.acc["pwd_salt"]):
            self.msg.config(text="El PIN no puede ser igual a la contraseña.", fg=TEXT_ERROR); return

        self.acc["pin"], self.acc["pin_salt"] = hash_password(nuevo)
        save_data(self.app.accounts)
        self.msg.config(text="✓ PIN cambiado con exito.", fg=TEXT_SUCCESS)
        self.app.after(1500, self.app.show_account_menu)