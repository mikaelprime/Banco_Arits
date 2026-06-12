import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import EMAIL_REMITENTE, EMAIL_PASSWORD, EMAIL_ADMIN, BANK_NAME

def enviar_solicitud_desbloqueo(usuario: str, motivo: str, explicacion: str) -> bool:
    try:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔒 [{BANK_NAME}] Solicitud de desbloqueo — {usuario}"
        msg["From"]    = EMAIL_REMITENTE
        msg["To"]      = EMAIL_ADMIN

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#0f0f1a;font-family:'Segoe UI',Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f0f1a;padding:30px 0;">
    <tr>
    <td align="center">
        <table width="580" cellpadding="0" cellspacing="0" style="background-color:#16213e;border-radius:16px;overflow:hidden;box-shadow:0 8px 32px rgba(0,180,216,0.15);">

        <!-- HEADER -->
        <tr>
            <td style="background:linear-gradient(135deg,#0f3460 0%,#1a1a2e 100%);padding:40px 40px 30px;text-align:center;border-bottom:3px solid #00b4d8;">
            <div style="font-size:48px;margin-bottom:10px;">🏦</div>
            <h1 style="margin:0;color:#00b4d8;font-size:26px;font-weight:700;letter-spacing:1px;">{BANK_NAME}</h1>
            <p style="margin:8px 0 0;color:#a8b2d8;font-size:13px;letter-spacing:2px;text-transform:uppercase;">Sistema de Notificaciones</p>
            </td>
        </tr>

        <!-- ALERTA -->
        <tr>
            <td style="padding:25px 40px 0;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#e6394620;border:1px solid #e63946;border-radius:10px;padding:15px;">
                <tr>
                <td style="padding:15px;">
                    <p style="margin:0;color:#e63946;font-size:15px;font-weight:700;">
                    🔒 &nbsp;SOLICITUD DE DESBLOQUEO DE CUENTA
                    </p>
                    <p style="margin:6px 0 0;color:#a8b2d8;font-size:13px;">
                    Un usuario requiere tu atención para reactivar su cuenta.
                    </p>
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <!-- DATOS -->
        <tr>
            <td style="padding:25px 40px;">
            <h2 style="margin:0 0 15px;color:#00b4d8;font-size:14px;letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid #0f3460;padding-bottom:10px;">
                📋 Datos de la Solicitud
            </h2>

            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                <td style="padding:10px 0;border-bottom:1px solid #0f3460;">
                    <span style="color:#a8b2d8;font-size:12px;text-transform:uppercase;letter-spacing:1px;">👤 Usuario</span><br>
                    <span style="color:#ffffff;font-size:16px;font-weight:600;">{usuario}</span>
                </td>
                </tr>
                <tr>
                <td style="padding:10px 0;border-bottom:1px solid #0f3460;">
                    <span style="color:#a8b2d8;font-size:12px;text-transform:uppercase;letter-spacing:1px;">📅 Fecha y hora</span><br>
                    <span style="color:#ffffff;font-size:15px;">{fecha}</span>
                </td>
                </tr>
                <tr>
                <td style="padding:10px 0;border-bottom:1px solid #0f3460;">
                    <span style="color:#a8b2d8;font-size:12px;text-transform:uppercase;letter-spacing:1px;">📌 Motivo</span><br>
                    <span style="color:#f4a261;font-size:15px;font-weight:600;">{motivo}</span>
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <!-- EXPLICACION -->
        <tr>
            <td style="padding:0 40px 25px;">
            <h2 style="margin:0 0 12px;color:#00b4d8;font-size:14px;letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid #0f3460;padding-bottom:10px;">
                📝 Explicación del Usuario
            </h2>
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f3460;border-radius:10px;border-left:4px solid #00b4d8;">
                <tr>
                <td style="padding:20px;">
                    <p style="margin:0;color:#ffffff;font-size:14px;line-height:1.7;">
                    {explicacion}
                    </p>
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <!-- ACCION -->
        <tr>
            <td style="padding:0 40px 30px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#0f3460,#1a1a2e);border:1px solid #00b4d8;border-radius:10px;">
                <tr>
                <td style="padding:20px;text-align:center;">
                    <p style="margin:0 0 8px;color:#00b4d8;font-size:13px;font-weight:700;letter-spacing:1px;text-transform:uppercase;">
                    ⚡ Acción Requerida
                    </p>
                    <p style="margin:0;color:#a8b2d8;font-size:13px;line-height:1.6;">
                    Ingresa al <strong style="color:#ffffff;">Panel de Administrador</strong> →
                    <strong style="color:#ffffff;">Reactivar cuenta bloqueada</strong><br>
                    y selecciona el usuario <strong style="color:#00b4d8;">{usuario}</strong>
                    </p>
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <!-- FOOTER -->
        <tr>
            <td style="background-color:#0f0f1a;padding:20px 40px;text-align:center;border-top:1px solid #0f3460;">
            <p style="margin:0;color:#a8b2d8;font-size:11px;">
                Este email fue generado automáticamente por <strong style="color:#00b4d8;">{BANK_NAME}</strong>
            </p>
            <p style="margin:6px 0 0;color:#4a5568;font-size:10px;">
                © 2026 {BANK_NAME} — Sistema de Seguridad
            </p>
            </td>
        </tr>

        </table>
    </td>
    </tr>
</table>

</body>
</html>
"""

        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
            server.sendmail(EMAIL_REMITENTE, EMAIL_ADMIN, msg.as_string())

        return True

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error enviando email: {e}")
        return False

def enviar_notificacion_login(usuario: str, fecha: str, email_usuario: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 [{BANK_NAME}] Inicio de sesión detectado"
        msg["From"]    = EMAIL_REMITENTE
        msg["To"]      = email_usuario

        html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#0f0f1a;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f0f1a;padding:30px 0;">
    <tr>
    <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="background-color:#16213e;border-radius:16px;overflow:hidden;box-shadow:0 8px 32px rgba(0,180,216,0.15);">

        <!-- HEADER -->
        <tr>
            <td style="background:linear-gradient(135deg,#0f3460,#1a1a2e);padding:35px 40px 25px;text-align:center;border-bottom:3px solid #00b4d8;">
            <div style="font-size:42px;margin-bottom:8px;">🏦</div>
            <h1 style="margin:0;color:#00b4d8;font-size:22px;font-weight:700;">{BANK_NAME}</h1>
            <p style="margin:6px 0 0;color:#a8b2d8;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Alerta de Seguridad</p>
            </td>
        </tr>

        <!-- ALERTA VERDE -->
        <tr>
            <td style="padding:25px 40px 0;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#2dc65320;border:1px solid #2dc653;border-radius:10px;">
                <tr>
                <td style="padding:15px;">
                    <p style="margin:0;color:#2dc653;font-size:15px;font-weight:700;">
                    ✅ &nbsp;INICIO DE SESIÓN EXITOSO
                    </p>
                    <p style="margin:6px 0 0;color:#a8b2d8;font-size:13px;">
                    Se detectó un acceso a tu cuenta bancaria.
                    </p>
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <!-- DATOS -->
        <tr>
            <td style="padding:25px 40px;">
            <h2 style="margin:0 0 15px;color:#00b4d8;font-size:13px;letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid #0f3460;padding-bottom:10px;">
                📋 Detalles del Acceso
            </h2>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                <td style="padding:10px 0;border-bottom:1px solid #0f3460;">
                    <span style="color:#a8b2d8;font-size:12px;text-transform:uppercase;letter-spacing:1px;">👤 Usuario</span><br>
                    <span style="color:#ffffff;font-size:16px;font-weight:600;">{usuario}</span>
                </td>
                </tr>
                <tr>
                <td style="padding:10px 0;">
                    <span style="color:#a8b2d8;font-size:12px;text-transform:uppercase;letter-spacing:1px;">📅 Fecha y hora</span><br>
                    <span style="color:#ffffff;font-size:15px;">{fecha}</span>
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <!-- ADVERTENCIA -->
        <tr>
            <td style="padding:0 40px 25px;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4a26120;border:1px solid #f4a261;border-radius:10px;">
                <tr>
                <td style="padding:15px;text-align:center;">
                    <p style="margin:0;color:#f4a261;font-size:13px;font-weight:700;">
                    ⚠️ ¿No fuiste tú?
                    </p>
                    <p style="margin:6px 0 0;color:#a8b2d8;font-size:12px;line-height:1.6;">
                    Si no reconoces este acceso, contacta al administrador<br>
                    inmediatamente para bloquear tu cuenta.
                    </p>
                </td>
                </tr>
            </table>
            </td>
        </tr>

        <!-- FOOTER -->
        <tr>
            <td style="background-color:#0f0f1a;padding:18px 40px;text-align:center;border-top:1px solid #0f3460;">
            <p style="margin:0;color:#a8b2d8;font-size:11px;">
                Mensaje automático de <strong style="color:#00b4d8;">{BANK_NAME}</strong>
            </p>
            <p style="margin:4px 0 0;color:#4a5568;font-size:10px;">
                © 2026 {BANK_NAME} — Sistema de Seguridad
            </p>
            </td>
        </tr>

        </table>
    </td>
    </tr>
</table>
</body>
</html>
"""

        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
            server.sendmail(EMAIL_REMITENTE, email_usuario, msg.as_string())
        return True

    except Exception as e:
        print(f"Error enviando notificación de login: {e}")
        return False