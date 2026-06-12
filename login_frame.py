"""Pantallas de login y crear cuenta."""

import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (BG_MAIN, BG_SECONDARY, BG_CARD, ACCENT, TEXT_PRIMARY,
                    TEXT_SECONDARY, FONT_TITLE, FONT_NORMAL, FONT_BTN,
                    FONT_SUBTITLE, TEXT_ERROR, TEXT_SUCCESS, FONT_SMALL,
                    EMAIL_ADMIN)
from security import verify_password, log_sospechoso
from email_service import enviar_notificacion_login
from data import save_data
from datetime import datetime
import time

class LoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_MAIN)
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Iniciar Sesion", font=FONT_TITLE,
                bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(30, 5))
        tk.Label(self, text="Ingresa tus credenciales",
                font=FONT_NORMAL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(pady=(0, 25))

        card = tk.Frame(self, bg=BG_CARD, padx=30, pady=30)
        card.pack(padx=40, fill="x")

        tk.Label(card, text="Usuario", font=FONT_NORMAL,
                bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")
        self.user_entry = self._make_entry(card)
        self.user_entry.pack(fill="x", pady=(3, 15))

        tk.Label(card, text="Contraseña", font=FONT_NORMAL,
                bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")
        self.pwd_entry = self._make_entry(card, show="●")
        self.pwd_entry.pack(fill="x", pady=(3, 20))

        self.msg_label = tk.Label(card, text="", font=FONT_SMALL,
                                bg=BG_CARD, fg=TEXT_ERROR, wraplength=380)
        self.msg_label.pack(pady=(0, 10))

        tk.Button(card, text="Iniciar Sesion", command=self._login,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=10,
                activebackground="#0096c7", activeforeground=TEXT_PRIMARY
                ).pack(fill="x", pady=(0, 10))

        tk.Button(card, text="← Volver", command=self.app.show_main_menu,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2",
                activebackground=BG_CARD, activeforeground=TEXT_PRIMARY
                ).pack()

        self.app.bind("<Return>", lambda e: self._login())

    def _make_entry(self, parent, show=None):
        e = tk.Entry(parent, font=FONT_NORMAL, bg="#1a1a2e", fg=TEXT_PRIMARY,
                    insertbackground=TEXT_PRIMARY, relief="flat",
                    highlightthickness=1, highlightbackground=ACCENT,
                    highlightcolor=ACCENT)
        if show:
            e.config(show=show)
        return e

    def _login(self):
        user = self.user_entry.get().strip()
        pwd  = self.pwd_entry.get().strip()
        acc  = self.app.accounts.get(user)

        if not user or not pwd:
            self.msg_label.config(text="Completa todos los campos.", fg=TEXT_ERROR)
            return

        if not acc:
            self.msg_label.config(text="Usuario o contraseña incorrecta.", fg=TEXT_ERROR)
            log_sospechoso("Intento login usuario inexistente", user)
            return

        if acc.get("bloqueado"):
            self.msg_label.config(
                text="Cuenta bloqueada. Contacta al administrador.", fg=TEXT_ERROR)
            if not hasattr(self, "_unlock_btn"):
                self._unlock_btn = tk.Button(
                    self, text="📩 Solicitar desbloqueo",
                    command=lambda u=user: self._show_unlock_form(u),
                    font=FONT_SMALL, bg="#e63946", fg=TEXT_PRIMARY,
                    relief="flat", cursor="hand2", pady=6,
                )
                self._unlock_btn.pack(pady=(5, 0))
            return

        intentos = self.app.login_attempts.get(user, 0)
        if intentos >= 3:
            self.msg_label.config(
                text="Demasiados intentos. Espera 20 segundos.", fg=TEXT_ERROR)
            self.app.after(20000, lambda: self._reset_attempts(user))
            return

        if verify_password(pwd, acc["pwd"], acc["pwd_salt"]):
            self.app.login_attempts[user] = 0
            acc["intentos_fallidos"] = 0
            acc["fecha_intentos"]    = ""
            ultimo = acc.get("ultimo_acceso", "")
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            acc["ultimo_acceso"] = fecha_actual
            save_data(self.app.accounts)
            self.app.current_user = user
            import threading
            email_usuario = acc.get("email", EMAIL_ADMIN)
            threading.Thread(
                target=enviar_notificacion_login,
                args=(user, fecha_actual, email_usuario),
                daemon=True
            ).start()
            self.app.show_account_menu()
        else:
            self.app.login_attempts[user] = intentos + 1
            hoy = datetime.now().strftime("%Y-%m-%d")
            if acc.get("fecha_intentos") != hoy:
                acc["intentos_fallidos"] = 0
                acc["fecha_intentos"]    = hoy
            acc["intentos_fallidos"] += 1
            log_sospechoso("Intento fallido de login", user)

            if acc["intentos_fallidos"] >= 5:
                acc["bloqueado"] = True
                save_data(self.app.accounts)
                log_sospechoso("Cuenta bloqueada por exceso de intentos", user)
                self.msg_label.config(
                    text="Cuenta bloqueada permanentemente. Contacta al administrador.", fg=TEXT_ERROR)
                return

            restantes = 3 - self.app.login_attempts[user]
            self.msg_label.config(
                text=f"Contraseña incorrecta. Intentos restantes: {restantes}", fg=TEXT_ERROR)
            self.pwd_entry.delete(0, "end")

    def _reset_attempts(self, user):
        self.app.login_attempts[user] = 0
        self.msg_label.config(text="Ya puedes intentar de nuevo.", fg=TEXT_SUCCESS)

    def _show_unlock_form(self, usuario):
        from UI.unlock_frame import UnlockFrame
        self.app.clear_screen()
        UnlockFrame(self.app.container, self.app, usuario).pack(
            fill="both", expand=True)

class CreateAccountFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_MAIN)
        self.app = app
        self._build()

    def _build(self):
        canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_MAIN)
        canvas.create_window((0, 0), window=inner, anchor="nw", width=520)

        tk.Label(inner, text="Crear Cuenta", font=FONT_TITLE,
                bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(30, 5))
        tk.Label(inner, text="Completa el formulario",
                font=FONT_NORMAL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(pady=(0, 20))

        card = tk.Frame(inner, bg=BG_CARD, padx=30, pady=25)
        card.pack(padx=40, fill="x")

        campos = [
            ("Usuario",           "user_e",    False),
            ("Correo electrónico","email_e",   False),
            ("Contraseña",        "pwd_e",     True),
            ("Depósito inicial",  "amount_e",  False),
            ("PIN (4 dígitos)",   "pin_e",     True),
        ]
        self.entries = {}
        for label, key, secret in campos:
            tk.Label(card, text=label, font=FONT_NORMAL,
                    bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")
            e = tk.Entry(card, font=FONT_NORMAL, bg="#1a1a2e", fg=TEXT_PRIMARY,
                        insertbackground=TEXT_PRIMARY, relief="flat",
                        highlightthickness=1, highlightbackground=ACCENT,
                        highlightcolor=ACCENT, show="●" if secret else "")
            e.pack(fill="x", pady=(3, 12))
            self.entries[key] = e

        self.msg_label = tk.Label(card, text="", font=FONT_SMALL,
                                bg=BG_CARD, fg=TEXT_ERROR, wraplength=380)
        self.msg_label.pack(pady=(0, 8))

        tk.Button(card, text="Crear Cuenta", command=self._create,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=10,
                activebackground="#0096c7", activeforeground=TEXT_PRIMARY
                ).pack(fill="x", pady=(0, 10))

        tk.Button(card, text="← Volver", command=self.app.show_main_menu,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2",
                activebackground=BG_CARD, activeforeground=TEXT_PRIMARY
                ).pack()

    def _create(self):
        import re
        from security import hash_password
        from data import record, save_data, save_user_file

        user   = self.entries["user_e"].get().strip()
        email  = self.entries["email_e"].get().strip()
        pwd    = self.entries["pwd_e"].get().strip()
        amount = self.entries["amount_e"].get().strip()
        pin    = self.entries["pin_e"].get().strip()

        if not user or not pwd or not amount or not pin or not email:
            self.msg_label.config(text="Completa todos los campos.", fg=TEXT_ERROR); return

        import re as _re
        if not _re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            self.msg_label.config(text="Correo electrónico inválido.", fg=TEXT_ERROR); return
        if not re.match(r'^[a-zA-Z0-9_]+$', user) or len(user) > 30:
            self.msg_label.config(text="Usuario invalido. Solo letras, números y _", fg=TEXT_ERROR); return
        if user in self.app.accounts:
            self.msg_label.config(text="Ese usuario ya existe.", fg=TEXT_ERROR); return
        if len(pwd) > 50:
            self.msg_label.config(text="Contraseña demasiado larga.", fg=TEXT_ERROR); return
        try:
            amt = float(amount.replace(",", "."))
            if amt != int(amt) or int(amt) < 0:
                raise ValueError
            amt = int(amt)
        except ValueError:
            self.msg_label.config(text="Deposito invalido. Solo numeros enteros.", fg=TEXT_ERROR); return
        if not pin.isdigit() or len(pin) < 4 :
            self.msg_label.config(text="PIN invalido. Debe ser numerico, 4 digitos.", fg=TEXT_ERROR); return
        if pwd == pin:
            self.msg_label.config(text="El PIN no puede ser igual a la contraseña.", fg=TEXT_ERROR); return

        pwd_hash, pwd_salt = hash_password(pwd)
        pin_hash, pin_salt = hash_password(pin)
        self.app.accounts[user] = {
            "user": user,
            "email": email,
            "pwd": pwd_hash, "pwd_salt": pwd_salt,
            "pin": pin_hash, "pin_salt": pin_salt,
            "balance": amt, "history": [],
            "bloqueado": False, "intentos_fallidos": 0,
            "fecha_intentos": "", "ultimo_acceso": "",
            "retiro_hoy": 0, "transferencia_hoy": 0,
            "fecha_limite": "",
        }
        record(self.app.accounts[user], "Deposito inicial", amt)
        save_data(self.app.accounts)
        save_user_file(self.app.accounts[user])
        self.msg_label.config(text="✓ Cuenta creada con exito.", fg=TEXT_SUCCESS)
        self.app.after(1500, self.app.show_main_menu)