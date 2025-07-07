# login/urls.py
from django.urls import path
from . import views # Mengimpor views dari aplikasi login

app_name = 'login'

urlpatterns = [
    path('', views.login_view, name='login'),         # URL: /login/
    path('logout/', views.logout_view, name='logout'), # URL: /login/logout/

    path('daftar/', views.register_view, name='daftar'), # URL: /login/logout/
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),  # ✅ Tambahan

    path('reset-password/', views.reset_password_request_view, name='reset_password_request'),
    path('reset-password/verify/', views.reset_password_verify_view, name='reset_password_verify'),
    path('reset-password/new/', views.reset_password_new_view, name='reset_password_new'),
]
