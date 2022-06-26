from django.core import mail
from config import settings
from smtplib import SMTP, SMTPServerDisconnected
from socket import gaierror


def send_mail(asunto: str, mensaje: str, *destinatarios: list, send=True) -> object:
    """ funcion que devuelve un objeto EmailMessage con un destinatario
     por defecto con las configuraciones hechas en el proyecto
     en settings.EMAIL_HOST_USER """
    email = mail.EmailMessage(asunto, mensaje, settings.FROM_USER, destinatarios)
    if send is True:
        email.send(fail_silently=True)
    else:
        return email


def test_connect_email() -> bool:
    try:
        smtp = SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        estado, msj = smtp.noop()
    except SMTPServerDisconnected:
        estado = -1
    except gaierror:
        estado = -2
    return True if estado == 250 else False



