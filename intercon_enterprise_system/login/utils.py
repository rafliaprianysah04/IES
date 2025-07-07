# login/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user_email, otp_code):
    subject = "Kode OTP Verifikasi Akun Anda"
    context = {
        'otp_code': otp_code,
        'year': datetime.now().year
    }

    html_content = render_to_string('login/otp_email.html', context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email='no-reply@intercon-terminal.com',
        to=[user_email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
