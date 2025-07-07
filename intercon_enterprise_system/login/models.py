# login/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

# Django's AbstractUser sudah menyediakan field dasar seperti:
# username, first_name, last_name, email, is_staff, is_active, date_joined.
# Field 'is_active' yang Anda sebutkan sudah ada dan berfungsi
# untuk menandai akun aktif (True) atau tidak (False).

class User(AbstractUser):
    """
    Model User kustom yang diperluas dari Django's AbstractUser.
    Menambahkan field 'role_id' sesuai permintaan.
    """
    # role_id: Field ini akan digunakan untuk menentukan level akses atau menu.
    # Untuk saat ini, kita mengaturnya sebagai IntegerField.
    # Dalam desain database yang lebih kompleks, ini bisa menjadi ForeignKey
    # ke model 'Role' yang terpisah.
    role_id = models.IntegerField(
        default=0, # Nilai default 0, bisa diartikan sebagai role 'umum' atau belum ditentukan
        verbose_name="ID Peran"
    )

    app_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="App ID"
    )

    class Meta:
        """
        Meta options untuk model User.
        """
        verbose_name = 'Pengguna'
        verbose_name_plural = 'Pengguna'

    def __str__(self):
        """
        Representasi string dari objek User.
        """
        return self.username

class OTPVerification(models.Model):
    user = models.ForeignKey('login.User', on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)  # 10 menit valid
