import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (BG_MAIN, BG_SECONDARY, BG_CARD, ACCENT, TEXT_PRIMARY,
                    TEXT_SECONDARY, FONT_TITLE, FONT_NORMAL, FONT_BTN,
                    FONT_SMALL, FONT_SUBTITLE, TEXT_ERROR, TEXT_SUCCESS,
                    TEXT_WARNING, CURRENCY_SYMBOL, ACCENT_HOVER)
from security import verify_password, hash_password, log_sospechoso
from data import save_data


class AdminLoginFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.configure(bg=BG_MAIN)
        self.app            = app
        self.admin_intentos = 0
        self._build()

    def _build(self):
        tk.Label(self, text="🛡️", font=("Segoe UI", 48),
                bg=BG_MAIN, fg=ACCENT).pack(pady=(40, 5))
        tk.Label(self, text="Panel de Administrador",
                font=FONT_TITLE, bg=BG_MAIN, fg=TEXT_PRIMARY).pack()
        tk.Label(self, text="Acceso Restringido",
                font=FONT_NORMAL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(pady=(0, 25))

        card = tk.Frame(self, bg=BG_CARD, padx=30, pady=30)
        card.pack(padx=60, fill="x")

        tk.Label(card, text="Clave de Administrador",
                font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")

        self.pwd_entry = tk.Entry(
            card, font=FONT_NORMAL, bg="#1a1a2e", fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY, relief="flat", show="●",
            highlightthickness=1, highlightbackground=ACCENT,
            highlightcolor=ACCENT)
        self.pwd_entry.pack(fill="x", pady=(3, 15))
        self.pwd_entry.bind("<Return>", lambda e: self._login())

        self.msg = tk.Label(card, text="", font=FONT_SMALL,
                            bg=BG_CARD, fg=TEXT_ERROR, wraplength=340)
        self.msg.pack(pady=(0, 10))

        tk.Button(card, text="Ingresar al panel", command=self._login,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=10,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_PRIMARY).pack(fill="x", pady=(0, 10))

        tk.Button(card, text="← Volver",
                command=self.app.show_main_menu,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2").pack()

    def _login(self):
        pwd = self.pwd_entry.get().strip()
        if not pwd:
            self.msg.config(text="Ingresa la clave.", fg=TEXT_ERROR)
            return

        if self.admin_intentos >= 3:
            self.msg.config(
                text="Demasiados intentos. Espera 20 segundos.", fg=TEXT_ERROR)
            self.app.after(20000, self._reset_intentos)
            return

        if verify_password(pwd, self.app.ADMIN_HASH, self.app.ADMIN_SALT):
            self.admin_intentos = 0
            self.app.show_admin_panel()
        else:
            self.admin_intentos += 1
            log_sospechoso("Intento fallido de acceso admin", "admin")
            restantes = 3 - self.admin_intentos
            if restantes > 0:
                self.msg.config(
                    text=f"Clave incorrecta. Intentos restantes: {restantes}",
                    fg=TEXT_ERROR)
            else:
                self.msg.config(text="Bloqueado por 20 segundos.", fg=TEXT_ERROR)
                self.app.after(20000, self._reset_intentos)
            self.pwd_entry.delete(0, "end")

    def _reset_intentos(self):
        self.admin_intentos = 0
        self.msg.config(text="Ya puedes intentar de nuevo.", fg=TEXT_SUCCESS)


class AdminPanelFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.configure(bg=BG_MAIN)
        self.app = app
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=BG_SECONDARY, pady=15)
        header.pack(fill="x")

        tk.Label(header, text="🛡️  Panel de Administrador",
                font=FONT_TITLE, bg=BG_SECONDARY, fg=TEXT_PRIMARY).pack()
        total      = len(self.app.accounts)
        bloqueadas = sum(1 for a in self.app.accounts.values() if a.get("bloqueado"))
        tk.Label(header,
                text=f"Cuentas: {total} total  |  {bloqueadas} bloqueadas",
                font=FONT_SMALL, bg=BG_SECONDARY, fg=TEXT_SECONDARY).pack(pady=(5, 0))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TNotebook", background=BG_MAIN, borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                        background=BG_CARD, foreground=TEXT_SECONDARY,
                        padding=(12, 6), font=("Segoe UI", 10))
        style.map("Custom.TNotebook.Tab",
                background=[("selected", ACCENT)],
                foreground=[("selected", TEXT_PRIMARY)])

        nb = ttk.Notebook(self, style="Custom.TNotebook")
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        tab_accounts = tk.Frame(nb, bg=BG_MAIN)
        nb.add(tab_accounts, text="👥 Cuentas")
        self._build_accounts_tab(tab_accounts)

        tab_actions = tk.Frame(nb, bg=BG_MAIN)
        nb.add(tab_actions, text="⚙️ Acciones")
        self._build_actions_tab(tab_actions)

        tab_log = tk.Frame(nb, bg=BG_MAIN)
        nb.add(tab_log, text="📜 Log")
        self._build_log_tab(tab_log)

        tk.Button(self, text="← Salir del panel",
                command=self.app.show_main_menu,
                font=FONT_BTN, bg="#2d2d44", fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=8,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_PRIMARY).pack(fill="x", padx=10, pady=(0, 10))

    def _build_accounts_tab(self, parent):
        style = ttk.Style()
        style.configure("Admin.Treeview",
                        background=BG_CARD, foreground=TEXT_PRIMARY,
                        fieldbackground=BG_CARD, rowheight=26,
                        font=("Segoe UI", 10))
        style.configure("Admin.Treeview.Heading",
                        background=BG_SECONDARY, foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Admin.Treeview",
                background=[("selected", ACCENT)],
                foreground=[("selected", TEXT_PRIMARY)])

        sb = ttk.Scrollbar(parent, orient="vertical")
        sb.pack(side="right", fill="y")

        cols = ("Usuario", "Saldo", "Movimientos", "Último acceso", "Estado")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings",
                                style="Admin.Treeview", yscrollcommand=sb.set)
        sb.config(command=self.tree.yview)

        anchos = [110, 90, 90, 150, 80]
        for col, ancho in zip(cols, anchos):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")

        self.tree.tag_configure("bloqueada", foreground="#e63946")
        self.tree.tag_configure("activa",    foreground=TEXT_SUCCESS)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self._load_accounts_table()

        tk.Button(parent, text="🔄 Actualizar",
                command=self._load_accounts_table,
                font=FONT_SMALL, bg=BG_CARD, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=5).pack(pady=5)

    def _load_accounts_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for user, acc in sorted(self.app.accounts.items()):
            estado = "BLOQUEADA" if acc.get("bloqueado") else "ACTIVA"
            tag    = "bloqueada" if acc.get("bloqueado") else "activa"
            self.tree.insert("", "end", values=(
                acc["user"],
                f"{CURRENCY_SYMBOL} {acc['balance']:.2f}",
                len(acc["history"]),
                acc.get("ultimo_acceso", "Sin registro"),
                estado,
            ), tags=(tag,))

    def _build_actions_tab(self, parent):
        acciones = acciones = [
            ("📩 Ver solicitudes de desbloqueo", self._view_solicitudes),
            ("🔓 Reactivar cuenta bloqueada",    self._reactivate),
            ("🔑 Resetear contraseña",           self._reset_password),
            ("🔐 Resetear PIN",                  self._reset_pin),
            ("📋 Ver historial de usuario",      self._view_history),
        ]
        for text, cmd in acciones:
            tk.Button(parent, text=text, command=cmd,
                    font=FONT_BTN, bg=BG_CARD, fg=TEXT_PRIMARY,
                    relief="flat", cursor="hand2", pady=10, anchor="w",
                    padx=20, activebackground=ACCENT_HOVER,
                    activeforeground=TEXT_PRIMARY).pack(fill="x", padx=20, pady=6)

    def _view_solicitudes(self):
        import json, os
        SOLICITUDES_DIR = "solicitudes"

        win = tk.Toplevel(self.app)
        win.title("Solicitudes de desbloqueo")
        win.geometry("560x480")
        win.configure(bg=BG_MAIN)

        tk.Label(win, text="📩 Solicitudes de Desbloqueo",
                font=FONT_SUBTITLE, bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(15, 5))

        frame = tk.Frame(win, bg=BG_MAIN)
        frame.pack(fill="both", expand=True, padx=10)

        sb = ttk.Scrollbar(frame, orient="vertical")
        sb.pack(side="right", fill="y")

        text = tk.Text(frame, font=("Consolas", 9),
                    bg=BG_CARD, fg=TEXT_PRIMARY,
                    relief="flat", state="normal",
                    yscrollcommand=sb.set, wrap="word")
        sb.config(command=text.yview)
        text.pack(fill="both", expand=True)

        try:
            archivos = sorted([
                f for f in os.listdir(SOLICITUDES_DIR)
                if f.endswith("_Solicitud.json")
            ])

            if not archivos:
                text.insert("end", "No hay solicitudes pendientes.")
            else:
                tk.Label(win, text=f"Total: {len(archivos)} usuario(s) con solicitudes",
                        font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(pady=(0, 5))

                for archivo in archivos:
                    path = os.path.join(SOLICITUDES_DIR, archivo)
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    text.insert("end",
                        f"{'='*50}\n"
                        f"👤 Usuario: {data['usuario']}\n"
                        f"{'='*50}\n"
                    )
                    for i, s in enumerate(reversed(data["solicitudes"]), 1):
                        text.insert("end",
                            f"  Solicitud #{i}\n"
                            f"  Fecha     : {s['fecha']}\n"
                            f"  Motivo    : {s['motivo']}\n"
                            f"  Estado    : {s['estado'].upper()}\n"
                            f"  Explicación:\n  {s['explicacion']}\n\n"
                        )

        except FileNotFoundError:
            text.insert("end", "No hay solicitudes pendientes.")

        text.config(state="disabled")

        tk.Button(win, text="Cerrar", command=win.destroy,
                font=FONT_BTN, bg=BG_CARD, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=6).pack(pady=10)

    def _reactivate(self):
        bloqueadas = [u for u, a in self.app.accounts.items() if a.get("bloqueado")]
        if not bloqueadas:
            messagebox.showinfo("Sin bloqueadas",
                                "No hay cuentas bloqueadas.", parent=self.app)
            return
        win = self._user_picker("Reactivar cuenta", bloqueadas, self._do_reactivate)
        win.grab_set()

    def _do_reactivate(self, user):
        self.app.accounts[user]["bloqueado"]         = False
        self.app.accounts[user]["intentos_fallidos"] = 0
        self.app.accounts[user]["fecha_intentos"]    = ""
        save_data(self.app.accounts)
        messagebox.showinfo("Éxito", f"Cuenta '{user}' reactivada.", parent=self.app)
        self._load_accounts_table()

    def _reset_password(self):
        self._admin_action_dialog(
            "Resetear contraseña",
            "Nueva contraseña temporal:",
            secret=True,
            on_confirm=self._do_reset_password)

    def _do_reset_password(self, user, value):
        if not value or len(value) > 50:
            messagebox.showerror("Error", "Contraseña inválida.", parent=self.app)
            return
        self.app.accounts[user]["pwd"], \
        self.app.accounts[user]["pwd_salt"] = hash_password(value)
        save_data(self.app.accounts)
        log_sospechoso("Admin reseteó contraseña", user)
        messagebox.showinfo("Éxito", f"Contraseña de '{user}' reseteada.", parent=self.app)

    def _reset_pin(self):
        self._admin_action_dialog(
            "Resetear PIN",
            "Nuevo PIN temporal (4 dígitos):",
            secret=True,
            on_confirm=self._do_reset_pin)

    def _do_reset_pin(self, user, value):
        if not value.isdigit() or len(value) < 4:
            messagebox.showerror("Error", "PIN inválido.", parent=self.app)
            return
        self.app.accounts[user]["pin"], \
        self.app.accounts[user]["pin_salt"] = hash_password(value)
        save_data(self.app.accounts)
        log_sospechoso("Admin reseteó PIN", user)
        messagebox.showinfo("Éxito", f"PIN de '{user}' reseteado.", parent=self.app)

    def _view_history(self):
        users = sorted(self.app.accounts.keys())
        if not users:
            messagebox.showinfo("Sin cuentas",
                                "No hay cuentas registradas.", parent=self.app)
            return
        self._user_picker("Ver historial", users, self._do_view_history)

    def _do_view_history(self, user):
        acc = self.app.accounts[user]
        win = tk.Toplevel(self.app)
        win.title(f"Historial — {user}")
        win.geometry("560x420")
        win.configure(bg=BG_MAIN)

        tk.Label(win, text=f"📋 Historial de {user}",
                font=FONT_SUBTITLE, bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(15, 3))
        tk.Label(win,
                text=f"Saldo: {CURRENCY_SYMBOL} {acc['balance']:.2f}  |  "
                    f"Movimientos: {len(acc['history'])}",
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(pady=(0, 10))

        frame = tk.Frame(win, bg=BG_MAIN)
        frame.pack(fill="both", expand=True, padx=10)

        sb = ttk.Scrollbar(frame, orient="vertical")
        sb.pack(side="right", fill="y")

        cols = ("Fecha", "Tipo", "Monto", "Saldo")
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            style="Admin.Treeview", yscrollcommand=sb.set)
        sb.config(command=tree.yview)

        tree.heading("Fecha", text="Fecha")
        tree.heading("Tipo",  text="Tipo")
        tree.heading("Monto", text="Monto")
        tree.heading("Saldo", text="Saldo")
        tree.column("Fecha", width=150, anchor="center")
        tree.column("Tipo",  width=180, anchor="w")
        tree.column("Monto", width=90,  anchor="e")
        tree.column("Saldo", width=90,  anchor="e")
        tree.tag_configure("pos", foreground=TEXT_SUCCESS)
        tree.tag_configure("neg", foreground="#e63946")
        tree.pack(fill="both", expand=True)

        for m in reversed(acc["history"]):
            sign = "+" if m["amount"] >= 0 else ""
            tag  = "pos" if m["amount"] >= 0 else "neg"
            tree.insert("", "end", values=(
                m["date"], m["type"],
                f"{sign}{CURRENCY_SYMBOL} {m['amount']:.2f}",
                f"{CURRENCY_SYMBOL} {m['balance']:.2f}",
            ), tags=(tag,))

        tk.Button(win, text="Cerrar", command=win.destroy,
                font=FONT_BTN, bg=BG_CARD, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=6).pack(pady=10)

    def _build_log_tab(self, parent):
        from config import LOG_FILE

        sb = ttk.Scrollbar(parent, orient="vertical")
        sb.pack(side="right", fill="y")

        self.log_text = tk.Text(
            parent, font=("Consolas", 9),
            bg="#0d0d1a", fg=TEXT_SUCCESS,
            relief="flat", state="disabled",
            yscrollcommand=sb.set, wrap="none")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        sb.config(command=self.log_text.yview)

        tk.Button(parent, text="🔄 Actualizar log",
                command=self._load_log,
                font=FONT_SMALL, bg=BG_CARD, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=5).pack(pady=5)

        self._load_log()

    def _load_log(self):
        from config import LOG_FILE
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            if lineas:
                for linea in lineas[-100:]:
                    self.log_text.insert("end", linea)
                self.log_text.see("end")
            else:
                self.log_text.insert("end", "No hay actividad registrada.")
        except FileNotFoundError:
            self.log_text.insert("end", "No hay actividad registrada.")
        self.log_text.config(state="disabled")

    def _user_picker(self, title, users, on_select):
        win = tk.Toplevel(self.app)
        win.title(title)
        win.geometry("300x380")
        win.configure(bg=BG_MAIN)

        tk.Label(win, text=title, font=FONT_SUBTITLE,
                bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(15, 10))

        listbox = tk.Listbox(win, font=FONT_NORMAL,
                            bg=BG_CARD, fg=TEXT_PRIMARY,
                            selectbackground=ACCENT,
                            selectforeground=TEXT_PRIMARY,
                            relief="flat", bd=0, highlightthickness=0)
        listbox.pack(fill="both", expand=True, padx=20, pady=5)
        for u in users:
            listbox.insert("end", u)

        def confirm():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Selecciona", "Elige un usuario.", parent=win)
                return
            user = listbox.get(sel[0])
            win.destroy()
            on_select(user)

        tk.Button(win, text="Confirmar", command=confirm,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=8).pack(fill="x", padx=20, pady=8)
        tk.Button(win, text="Cancelar", command=win.destroy,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2").pack()
        return win

    def _admin_action_dialog(self, title, field_label, secret=False, on_confirm=None):
        win = tk.Toplevel(self.app)
        win.title(title)
        win.geometry("320x300")
        win.configure(bg=BG_MAIN)

        tk.Label(win, text=title, font=FONT_SUBTITLE,
                bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(15, 10))

        tk.Label(win, text="Usuario:", font=FONT_NORMAL,
                bg=BG_MAIN, fg=TEXT_SECONDARY).pack(anchor="w", padx=25)
        user_var = tk.StringVar()
        users    = sorted(self.app.accounts.keys())
        combo    = ttk.Combobox(win, textvariable=user_var,
                                values=users, state="readonly", font=FONT_NORMAL)
        combo.pack(fill="x", padx=25, pady=(3, 12))

        tk.Label(win, text=field_label, font=FONT_NORMAL,
                bg=BG_MAIN, fg=TEXT_SECONDARY).pack(anchor="w", padx=25)
        val_entry = tk.Entry(win, font=FONT_NORMAL,
                            bg="#1a1a2e", fg=TEXT_PRIMARY,
                            insertbackground=TEXT_PRIMARY,
                            relief="flat", show="●" if secret else "",
                            highlightthickness=1, highlightbackground=ACCENT)
        val_entry.pack(fill="x", padx=25, pady=(3, 15))

        def confirm():
            user = user_var.get().strip()
            val  = val_entry.get().strip()
            if not user or user not in self.app.accounts:
                messagebox.showerror("Error", "Selecciona un usuario válido.", parent=win)
                return
            win.destroy()
            if on_confirm:
                on_confirm(user, val)

        tk.Button(win, text="Confirmar", command=confirm,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=8).pack(fill="x", padx=25, pady=(0, 8))
        tk.Button(win, text="Cancelar", command=win.destroy,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2").pack()