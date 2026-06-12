import tkinter as tk
from tkinter import messagebox
import sys, os
from turtle import fill
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (BG_MAIN, BG_SECONDARY, BG_CARD, ACCENT, TEXT_PRIMARY,
                    TEXT_SECONDARY, FONT_TITLE, FONT_NORMAL, FONT_BTN,
                    FONT_SUBTITLE, TEXT_ERROR, TEXT_SUCCESS, FONT_SMALL,
                    TEXT_WARNING, CURRENCY_SYMBOL, ACCENT_HOVER)

class AccountMenuFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.configure(bg=BG_MAIN)
        self.app = app
        self.acc = app.accounts.get(app.current_user)
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=BG_SECONDARY, pady=20 )
        header.pack(fill="x")
        
        tk.Label(header, text="👤", font=("Segoe UI", 28),
                bg=BG_SECONDARY, fg=ACCENT).pack()
        tk.Label(header, text=f"Hola, {self.app.current_user}",
                font=FONT_TITLE, bg=BG_SECONDARY, fg=TEXT_PRIMARY).pack()
        
        self.saldo_label = tk.Label(
            header,
            text=f"{CURRENCY_SYMBOL} {self.acc["balance"]:.2f}",
            font=("Segoe UI", 20, "bold"),
            bg=BG_SECONDARY, fg=ACCENT
            )
        self.saldo_label.pack(pady=(5, 0))
        tk.Label(header, text="Saldo disponible",
                font=FONT_SMALL, bg=BG_SECONDARY, fg=TEXT_SECONDARY).pack()
        from config import LIMITE_RETIRO_DIARIO, LIMITE_TRANSFERENCIA_DIARIA
        from datetime import datetime
        hoy = datetime.now().strftime("%Y-%m-%d")
        if self.acc.get("fecha_limite") == hoy:
            retiro_usado       = self.acc.get("retiro_hoy", 0)
            transfer_usado     = self.acc.get("transferencia_hoy", 0)
        else:
            retiro_usado       = 0
            transfer_usado     = 0

        tk.Label(header,
                text=f"Retiro hoy: $ {retiro_usado:.2f} / $ {LIMITE_RETIRO_DIARIO:.2f}  |  "
                    f"Transferencia hoy: $ {transfer_usado:.2f} / $ {LIMITE_TRANSFERENCIA_DIARIA:.2f}",
                font=FONT_SMALL, bg=BG_SECONDARY, fg=TEXT_SECONDARY).pack(pady=(3, 0))
        
        btn_frame = tk.Frame(self, bg=BG_MAIN, pady=15)
        btn_frame.pack(fill="both", expand=True, padx=40)

        canvas = tk.Canvas(btn_frame, bg=BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(btn_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG_MAIN)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_resize(e):
            canvas.itemconfig(canvas_window, width=e.width)
        canvas.bind("<Configure>", on_resize)

        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", on_frame_configure)

        botones = [
            ("💰  Depositar",          self._show_deposit,    ACCENT),
            ("💸  Retirar",            self._show_withdraw,   BG_CARD),
            ("🔁  Transferir",         self._show_transfer,   BG_CARD),
            ("📋  Historial",          self._show_history,    BG_CARD),
            ("🔑  Cambiar contraseña", self._show_change_pwd, BG_CARD),
            ("🔐  Cambiar PIN",        self._show_change_pin, BG_CARD),
            ("🚪  Cerrar sesión",      self._logout,          "#2d2d44"),
        ]

        for text, cmd, color in botones:
            tk.Button(
                inner, text=text, command=cmd,
                font=FONT_BTN, bg=color, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=8, anchor="w",
                padx=20, activebackground=ACCENT_HOVER,
                activeforeground=TEXT_PRIMARY, bd=0
            ).pack(fill="x", pady=4)

        def on_mousewheel(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def _refresh_saldo(self):
        self.saldo_label.config(
            text=f"{CURRENCY_SYMBOL} {self.acc["balance"]:.2f}")

    def _show_deposit(self):
        from UI.operations_frame import OperationFrame
        self.app.clear_screen()
        OperationFrame(self.app.container, self.app, "deposit").pack(
            fill="both", expand=True)

    def _show_withdraw(self):
        from UI.operations_frame import OperationFrame
        self.app.clear_screen()
        OperationFrame(self.app.container, self.app, "withdraw").pack(
            fill="both", expand=True)

    def _show_transfer(self):
        from UI.operations_frame import OperationFrame
        self.app.clear_screen()
        OperationFrame(self.app.container, self.app, "transfer").pack(
            fill="both", expand=True)

    def _show_history(self):
        from UI.history_frame import HistoryFrame
        self.app.clear_screen()
        HistoryFrame(self.app.container, self.app).pack(
            fill="both", expand=True)

    def _show_change_pwd(self):
        from UI.operations_frame import ChangePasswordFrame
        self.app.clear_screen()
        ChangePasswordFrame(self.app.container, self.app).pack(
            fill="both", expand=True)

    def _show_change_pin(self):
        from UI.operations_frame import ChangePinFrame
        self.app.clear_screen()
        ChangePinFrame(self.app.container, self.app).pack(
            fill="both", expand=True)

    def _logout(self):
        from data import save_data
        save_data(self.app.accounts)
        self.app.current_user = None
        self.app.show_main_menu()