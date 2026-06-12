import tkinter as tk
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (BG_MAIN, BG_SECONDARY, BG_CARD, ACCENT, TEXT_PRIMARY,
                    TEXT_SECONDARY, FONT_TITLE, FONT_NORMAL, FONT_BTN,
                    FONT_SMALL, TEXT_ERROR, TEXT_SUCCESS, TEXT_WARNING,
                    CURRENCY_SYMBOL, ACCENT_HOVER)

class HistoryFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_MAIN)
        self.app = app
        self.acc = app.accounts.get(app.current_user)
        self.filter_type = tk.StringVar(value="Todos")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=BG_SECONDARY, pady=15)
        header.pack(fill="x")
        
        tk.Label(header, text="📋  Historial de Movimientos",
                font=FONT_TITLE, bg=BG_SECONDARY, fg=TEXT_PRIMARY).pack()
        tk.Label(header,
                text=f"Saldo actual: {CURRENCY_SYMBOL} {self.acc['balance']:.2f}",
                font=FONT_NORMAL, bg=BG_SECONDARY, fg=ACCENT).pack(pady=(5, 0))
        
        filter_frame = tk.Frame(self, bg=BG_MAIN, pady=10)
        filter_frame.pack(fill="x", padx=40)
        
        tk.Label(filter_frame, text="Filtrar por: ",
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(side="left", padx=(0, 10))
        
        tipos = ["Todos", "Deposito", "Retiro",
                "Transferencia Enviada", "Transferencia Recibida",
                "Deposito Inicial"]
        
        for tipo in tipos:
            rb = tk.Radiobutton(
                filter_frame, text=tipo,
                variable=self.filter_type, value=tipo,
                command=self._apply_filter,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                selectcolor=BG_CARD, activebackground=BG_MAIN,
                activeforeground=ACCENT, cursor="hand2",
                indicatoron=False, relief="flat",
                padx=8, pady=4,
                highlightthickness=0,
            )
            rb.bind("<Button-1>", lambda e, t=tipo: [
                self.filter_type.set(t),
                self._apply_filter()
            ])
            rb.pack(side="left", padx=2)
            
            table_frame = tk.Frame(self, bg=BG_MAIN)
            table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=BG_CARD,
                        foreground=TEXT_PRIMARY,
                        fieldbackground=BG_CARD,
                        rowheight=28,
                        font=("Segoe UI", 10))
        style.configure("Custom.Treeview.Heading",
                        background=BG_SECONDARY,
                        foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Custom.Treeview",
                background=[("selected", ACCENT)],
                foreground=[("selected", TEXT_PRIMARY)])
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        cols = ("Fecha", "Tipo", "Monto", "Saldo")
        self.tree = ttk.Treeview(
            table_frame, columns=cols, show="headings",
            style="Custom.Treeview",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading("Fecha",  text="📅 Fecha")
        self.tree.heading("Tipo",   text="📌 Tipo")
        self.tree.heading("Monto",  text="💲 Monto")
        self.tree.heading("Saldo",  text="💰 Saldo")

        self.tree.column("Fecha",  width=150, anchor="center")
        self.tree.column("Tipo",   width=180, anchor="w")
        self.tree.column("Monto",  width=90,  anchor="e")
        self.tree.column("Saldo",  width=90,  anchor="e")

        self.tree.pack(fill="both", expand=True)
        
        self.tree.tag_configure("positivo", foreground=TEXT_SUCCESS)
        self.tree.tag_configure("negativo", foreground="#e63946")
        self.tree.tag_configure("neutro",   foreground=TEXT_SECONDARY)
        
        self.summary_frame = tk.Frame(self, bg=BG_SECONDARY, pady=8)
        self.summary_frame.pack(fill="x", padx=20, pady=(0, 5))

        self.summary_label = tk.Label(
            self.summary_frame, text="",
            font=FONT_SMALL, bg=BG_SECONDARY, fg=TEXT_SECONDARY)
        self.summary_label.pack()
        
        tk.Button(self, text="← Volver al menú",
                command=self.app.show_account_menu,
                font=FONT_BTN, bg=BG_CARD, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=8,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_PRIMARY
                ).pack(fill="x", padx=20, pady=(0, 10))
        
        self._apply_filter()
        
    def _apply_filter(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtro   = self.filter_type.get()
        historial = self.acc.get("history", [])

        if filtro != "Todos":
            historial = [m for m in historial if m["type"] == filtro]

        if not historial:
            self.tree.insert("", "end",
                            values=("—", "Sin movimientos", "—", "—"),
                            tags=("neutro",))
            self.summary_label.config(text="No hay movimientos para este filtro.")
            return

        total_entradas = 0
        total_salidas  = 0

        for m in reversed(historial):
            sign  = "+" if m["amount"] >= 0 else ""
            monto = f"{sign}{CURRENCY_SYMBOL} {m['amount']:.2f}"
            saldo = f"{CURRENCY_SYMBOL} {m['balance']:.2f}"
            tag   = "positivo" if m["amount"] >= 0 else "negativo"

            self.tree.insert("", "end",
                            values=(m["date"], m["type"], monto, saldo),
                            tags=(tag,))

            if m["amount"] >= 0:
                total_entradas += m["amount"]
            else:
                total_salidas  += abs(m["amount"])

        total_movs = len(historial)
        self.summary_label.config(
            text=(f"Total: {total_movs} movimiento(s)  |  "
                f"Entradas: {CURRENCY_SYMBOL} {total_entradas:.2f}  |  "
                f"Salidas: {CURRENCY_SYMBOL} {total_salidas:.2f}"),
            fg=TEXT_SECONDARY
        )