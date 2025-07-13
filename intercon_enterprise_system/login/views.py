from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from .forms import LoginForm, RegisterForm
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from .models import User, OTPVerification
from .utils import generate_otp, send_otp_email
from django.utils import timezone
from django.views.decorators.http import require_http_methods

def api_login(request):
    username = request.GET.get('username')
    password = request.GET.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return JsonResponse({'error': 'Invalid credentials'}, status=401)


def login_view(request):
    """
    View untuk menangani proses login pengguna.
    Superadmin akan diarahkan ke app_partition dengan semua menu,
    sedangkan role lain (misal finance) diarahkan ke app_partition terbatas.
    """
    if request.user.is_authenticated:
        return redirect(reverse('app_partition:app_view'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not remember:
                        request.session.set_expiry(0)

                    # Setelah login berhasil, arahkan ke app_partition
                    return redirect(reverse('app_partition:app_view'))
                else:
                    messages.error(request, "Akun Anda tidak aktif. Silakan hubungi administrator.")
            else:
                messages.error(request, "Email atau password salah.")
        else:
            messages.error(request, "Silakan periksa kembali input Anda.")
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})

def verify_otp_view(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        user_id = request.session.get('pending_user_id')

        try:
            otp_record = OTPVerification.objects.filter(
                user_id=user_id,
                is_verified=False,
                otp_code=otp_input
            ).latest('created_at')  # ✅ Ambil OTP terakhir
            if not otp_record.is_expired():
                otp_record.is_verified = True
                otp_record.save()

                user = otp_record.user
                user.is_active = True
                user.save()

                del request.session['pending_user_id']
                messages.success(request, "Akun berhasil diverifikasi, silakan login.")
                return redirect('login:login')
            else:
                messages.error(request, "Kode OTP telah kedaluwarsa.")
        except OTPVerification.DoesNotExist:
            messages.error(request, "Kode OTP tidak valid.")

    return render(request, 'login/verify_otp.html')

@require_http_methods(["GET"])  # Ubah dari POST ke GET
def resend_otp_view(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.error(request, "Tidak dapat mengirim ulang OTP. Silakan daftar ulang.")
        return redirect('login:daftar')

    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "Pengguna tidak ditemukan.")
        return redirect('login:daftar')

    new_otp = generate_otp()

    OTPVerification.objects.update_or_create(
        user=user,
        is_verified=False,
        defaults={
            'otp_code': new_otp,
            'created_at': timezone.now()
        }
    )

    send_otp_email(user.email, new_otp)
    messages.success(request, "Kode OTP baru telah dikirim ke email Anda.")
    return redirect('login:verify_otp')

def register_view(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=f"{form.cleaned_data['first_name']}.{form.cleaned_data['last_name']}".lower(),
                password=form.cleaned_data['password'],
                is_staff=True,
                is_active=False,
                role_id=3,
                app_id='finance'
            )

            otp = generate_otp()

            OTPVerification.objects.update_or_create(
                user=user,
                is_verified=False,
                defaults={
                    'otp_code': otp,
                    'created_at': timezone.now()
                }
            )

            send_otp_email(user.email, otp)
            request.session['pending_user_id'] = user.id

            return redirect('login:verify_otp')

    return render(request, 'login/register.html', {'form': form})

def reset_password_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp_input = request.POST.get('otp')

        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "Email tidak ditemukan.")
            return redirect('login:reset_password_request')

        if otp_input:
            try:
                # ✅ Ambil OTP terakhir yang belum diverifikasi
                otp_record = OTPVerification.objects.filter(
                    user=user,
                    is_verified=False,
                    otp_code=otp_input
                ).latest('created_at')

                if not otp_record.is_expired():
                    otp_record.is_verified = True
                    otp_record.save()
                    request.session['reset_user_id'] = user.id
                    messages.success(request, "OTP valid. Silakan atur ulang password Anda.")
                    return redirect('login:reset_password_form')
                else:
                    messages.error(request, "Kode OTP sudah kedaluwarsa.")
            except OTPVerification.DoesNotExist:
                messages.error(request, "Kode OTP tidak valid.")
        else:
            otp = generate_otp()
            OTPVerification.objects.create(user=user, otp_code=otp)
            send_otp_email(user.email, otp)

            # Simpan ID user di session agar bisa digunakan di halaman verifikasi OTP
            request.session['reset_user_id'] = user.id

            messages.success(request, "Kode OTP telah dikirim ke email Anda.")
            return redirect('login:reset_password_verify')  # arahkan ke halaman verifikasi

    return render(request, 'login/reset_password_request.html')

def reset_password_verify_view(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        user_id = request.session.get('reset_user_id')

        try:
            user = User.objects.get(id=user_id)  # ✅ Tambahkan ini

            otp_record = OTPVerification.objects.filter(user=user, otp_code=otp_input, is_verified=False).latest('created_at')
            if not otp_record.is_expired():
                otp_record.is_verified = True
                otp_record.save()

                request.session['allow_password_reset'] = True  # Digunakan untuk proteksi view reset password baru
                messages.success(request, "OTP berhasil diverifikasi. Silakan atur ulang password Anda.")
                return redirect('login:reset_password_new')
            else:
                messages.error(request, "Kode OTP telah kedaluwarsa.")
        except OTPVerification.DoesNotExist:
            messages.error(request, "Kode OTP tidak valid.")
        except User.DoesNotExist:
            messages.error(request, "Pengguna tidak ditemukan.")

    return render(request, 'login/reset_password_verify.html')

def reset_password_new_view(request):
    if not request.session.get('allow_password_reset'):
        return redirect('login:reset_password_request')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_id = request.session.get('reset_user_id')

        if password1 != password2:
            messages.error(request, "Password tidak cocok.")
        else:
            user = User.objects.get(id=user_id)
            user.set_password(password1)
            user.save()

            # Bersihkan session
            del request.session['reset_user_id']
            del request.session['allow_password_reset']

            messages.success(request, "Password berhasil diperbarui. Silakan login.")
            return redirect('login:login')

    return render(request, 'login/reset_password_new.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Anda telah berhasil logout.")
    return redirect(reverse('login:login'))
