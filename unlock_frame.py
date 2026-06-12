import tkinter as tk
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (BG_MAIN, BG_CARD, BG_SECONDARY, ACCENT, TEXT_PRIMARY,
                    TEXT_SECONDARY, FONT_TITLE, FONT_NORMAL, FONT_BTN,
                    FONT_SMALL, TEXT_ERROR, TEXT_SUCCESS, ACCENT_HOVER)
from data import guardar_solicitud
from email_service import enviar_solicitud_desbloqueo

MOTIVOS = [
    "Olvidé mi contraseña",
    "Demasiados intentos fallidos accidentales",
    "Alguien intentó acceder sin mi permiso",
    "Error del sistema",
    "Otro motivo",
]

class UnlockFrame(tk.Frame):
    def __init__(self, parent, app, usuario):
        super().__init__(parent)
        self.configure(bg=BG_MAIN)
        self.app     = app
        self.usuario = usuario
        self._build()

    def _build(self):
        tk.Label(self, text="📩  Solicitar Desbloqueo",
            font=FONT_TITLE, bg=BG_MAIN, fg=TEXT_PRIMARY).pack(pady=(25, 5))
        tk.Label(self,
                text=f"Cuenta: {self.usuario}",
                font=FONT_NORMAL, bg=BG_MAIN, fg=TEXT_SECONDARY).pack(pady=(0, 20))

        card = tk.Frame(self, bg=BG_CARD, padx=30, pady=25)
        card.pack(padx=40, fill="x")

        tk.Label(card, text="Motivo del bloqueo",
                font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")

        self.motivo_var = tk.StringVar(value=MOTIVOS[0])
        combo = ttk.Combobox(card, textvariable=self.motivo_var,
                            values=MOTIVOS, state="readonly",
                            font=FONT_NORMAL)
        combo.pack(fill="x", pady=(3, 15))

        tk.Label(card, text="Explica lo que pasó",
                font=FONT_NORMAL, bg=BG_CARD, fg=TEXT_SECONDARY).pack(anchor="w")

        self.texto = tk.Text(card, font=FONT_NORMAL,
                            bg="#1a1a2e", fg=TEXT_PRIMARY,
                            insertbackground=TEXT_PRIMARY,
                            relief="flat", height=5,
                            highlightthickness=1,
                            highlightbackground=ACCENT,
                            highlightcolor=ACCENT)
        self.texto.pack(fill="x", pady=(3, 15))

        self.msg = tk.Label(card, text="", font=FONT_SMALL,
                            bg=BG_CARD, fg=TEXT_ERROR, wraplength=380)
        self.msg.pack(pady=(0, 8))

        tk.Button(card, text="📨 Enviar solicitud",
                command=self._enviar,
                font=FONT_BTN, bg=ACCENT, fg=TEXT_PRIMARY,
                relief="flat", cursor="hand2", pady=10,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_PRIMARY
                ).pack(fill="x", pady=(0, 10))

        tk.Button(card, text="← Volver",
                command=self.app.show_main_menu,
                font=FONT_SMALL, bg=BG_MAIN, fg=TEXT_SECONDARY,
                relief="flat", cursor="hand2"
                ).pack()

    def _enviar(self):
        motivo      = self.motivo_var.get().strip()
        explicacion = self.texto.get("1.0", "end").strip()

        if not explicacion:
            self.msg.config(
                text="Por favor explica lo que pasó.", fg=TEXT_ERROR)
            return

        if len(explicacion) < 20:
            self.msg.config(
                text="La explicación es muy corta. Mínimo 20 caracteres.",
                fg=TEXT_ERROR)
            return

        self.msg.config(text="Enviando solicitud...", fg=TEXT_SECONDARY)
        self.update()

        guardar_solicitud(self.usuario, motivo, explicacion)

        exito = enviar_solicitud_desbloqueo(self.usuario, motivo, explicacion)

        if exito:
            self.msg.config(
                text="✓ Solicitud enviada. El admin revisará tu caso.",
                fg=TEXT_SUCCESS)
            self.app.after(2500, self.app.show_main_menu)
        else:
            self.msg.config(
                text="⚠ Solicitud guardada pero el email falló.\n"
                    "Contacta al admin directamente.",
                fg=TEXT_ERROR)