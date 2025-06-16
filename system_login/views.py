from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

User = get_user_model()
otp_store = {}

# ==============================
# ✅ Fungsi login yang ingin diuji
# ==============================

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)

            # Redirect berdasarkan role
            if user.role == 'gate':
                return redirect('gate_in_out:dashboard')
            elif user.role == 'surveyor':
                return redirect('surveyor:dashboard') 
            elif user.role == 'estimator':
                return redirect('estimator:dashboard')
            elif user.role == 'qc':
                return redirect('quality_control:dashboard')
            elif user.role == 'cs':
                return redirect('customer_service:dashboard')
            elif user.role == 'consignee':
                return redirect('consignee:dashboard')
            else:
                messages.error(request, 'User tidak dikenali.')
                logout(request)
                return redirect('login_sistem:login')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'system_login/login.html')

def logout_view(request):
    logout(request)
    return redirect('login_sistem:login')

def register_view(request):
    if request.method == 'POST':
        firstname = request.POST.get("first_name")
        lastname = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = 'consignee'

        username = f"{firstname}.{lastname}".lower()  # 👈 generate username dari firstname dan lastname

        if password != password2:
            messages.error(request, 'Password tidak cocok.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah digunakan.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                first_name=firstname,
                last_name=lastname
            )
            # 👇 Tambahkan ini sebelum login
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Atau 'system_login.backends.EmailBackend' kalau kamu mau pakai itu

            login(request, user)
            return redirect('login_sistem:login')
    return render(request, 'system_login/register.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            otp = get_random_string(6, allowed_chars='0123456789')
            otp_store[email] = {'otp': otp, 'user_id': user.id}
            request.session['reset_email'] = email

            # Kirim email OTP
            subject = 'Kode OTP Reset Password'
            from_email = 'no-reply@intercon.com'
            to = [email]
            text_content = f'Kode OTP Anda adalah: {otp}'
            html_content = render_to_string('system_login/email_otp_template.html', {'otp': otp, 'email': email})

            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return redirect('login_sistem:verify_otp')

        except User.DoesNotExist:
            messages.error(request, 'Email tidak ditemukan.')

    return render(request, 'system_login/forgot_password.html')


def verify_otp_view(request):
    email = request.session.get('reset_email')
    if not email or email not in otp_store:
        return redirect('login_sistem:forgot_password')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        if otp_input == otp_store[email]['otp']:
            request.session['verified_user_id'] = otp_store[email]['user_id']
            return redirect('login_sistem:reset_password')
        else:
            messages.error(request, 'Kode OTP salah.')
    return render(request, 'system_login/verify_otp.html')

def reset_password_view(request):
    user_id = request.session.get('verified_user_id')
    if not user_id:
        return redirect('login_sistem:forgot_password')

    if request.method == 'POST':
        pwd1 = request.POST.get("new_password1")
        pwd2 = request.POST.get("new_password2")
        if pwd1 != pwd2:
            messages.error(request, 'Password tidak cocok.')
        else:
            user = User.objects.get(id=user_id)
            user.set_password(pwd1)
            user.save()
            messages.success(request, 'Password berhasil direset.')
            return redirect('login_sistem:login')
    return render(request, 'system_login/reset_password.html')

# ==============================
# ❌ Fungsi lain dikomentari sementara
# ==============================

'''
'''
