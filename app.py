import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (BG_MAIN, BG_SECONDARY, BG_CARD, ACCENT, FONT_SMALL, TEXT_PRIMARY,
                    TEXT_SECONDARY, FONT_TITLE, FONT_NORMAL, FONT_BTN,
                    FONT_SUBTITLE, TEXT_ERROR, TEXT_SUCCESS, TEXT_WARNING,
                    ACCENT_HOVER)

from data import load_data, save_data, initialize_accounts_dir
from security import get_admin_password_hash

class BancoApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Banco Arits")
        self.geometry("520x620")
        self.resizable(False, False)
        self.configure(bg=BG_MAIN)
        self._center_window()

        initialize_accounts_dir()
        self.accounts       = load_data()
        self.login_attempts = {}
        self.pin_attempts   = {}
        self.current_user   = None
        self.ADMIN_HASH, self.ADMIN_SALT = get_admin_password_hash()

        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(fill="both", expand=True)

        self.show_main_menu()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self):
        self.update_idletasks()
        w, h = 520, 620
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_screen()
        self.current_user = None

        header_frame = tk.Frame(self.container, bg=BG_SECONDARY, pady=30)
        header_frame.pack(fill="x")

        tk.Label(header_frame, text="🏦", font=("Segoe UI", 48),
                bg=BG_SECONDARY, fg=ACCENT).pack()
        tk.Label(header_frame, text="Banco Arits",
                font=FONT_TITLE, bg=BG_SECONDARY, fg=TEXT_PRIMARY).pack()
        tk.Label(header_frame, text="Tu banco de confianza",
                font=FONT_NORMAL, bg=BG_SECONDARY, fg=TEXT_SECONDARY).pack(pady=(0, 10))

        btn_frame = tk.Frame(self.container, bg=BG_MAIN, pady=40)
        btn_frame.pack(fill="both", expand=True)

        self._make_button(btn_frame, "Iniciar Sesión",
                        self.show_login, ACCENT).pack(pady=10)
        self._make_button(btn_frame, "Crear Cuenta",
                        self.show_create_account, BG_CARD).pack(pady=10)
        self._make_button(btn_frame, "Panel Admin",
                        self.show_admin_login, "#2d2d44").pack(pady=10)
        self._make_button(btn_frame, "Salir",
                        self._on_close, "#3d1515").pack(pady=10)

        tk.Label(self.container, text="© 2026 Banco Arits — Todos los derechos reservados",
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(side="bottom", pady=10)

    def show_login(self):
        from UI.login_frame import LoginFrame
        self.clear_screen()
        LoginFrame(self.container, self).pack(fill="both", expand=True)

    def show_create_account(self):
        from UI.login_frame import CreateAccountFrame
        self.clear_screen()
        CreateAccountFrame(self.container, self).pack(fill="both", expand=True)

    def show_account_menu(self):
        from UI.menu_frame import AccountMenuFrame
        self.clear_screen()
        AccountMenuFrame(self.container, self).pack(fill="both", expand=True)

    def show_admin_login(self):
        from UI.admin_frame import AdminLoginFrame
        self.clear_screen()
        AdminLoginFrame(self.container, self).pack(fill="both", expand=True)

    def show_admin_panel(self):
        from UI.admin_frame import AdminPanelFrame
        self.clear_screen()
        AdminPanelFrame(self.container, self).pack(fill="both", expand=True)

    def _make_button(self, parent, text, command, color):
        btn = tk.Button(
            parent, text=text, command=command,
            font=FONT_BTN, bg=color, fg=TEXT_PRIMARY,
            relief="flat", cursor="hand2",
            width=22, pady=10,
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_PRIMARY,
            bd=0
        )
        return btn

    def show_message(self, parent, text, color, pady=5):
        lbl = tk.Label(parent, text=text, font=FONT_SMALL,
                    bg=BG_MAIN, fg=color, wraplength=400)
        lbl.pack(pady=pady)
        return lbl

    def _on_close(self):
        save_data(self.accounts)
        self.destroy()