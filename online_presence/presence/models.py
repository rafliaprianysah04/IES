# presence/models.py
from django.db import models

# Model penghubung ke tabel existing
class ExternalMenu(models.Model):
    nama_menu = models.CharField(max_length=100)
    icon_menu = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    sort = models.IntegerField()
    app_id = models.CharField(max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'superadmin_menu'

class ExternalSubMenu(models.Model):
    nama_submenu = models.CharField(max_length=100)
    icon_submenu = models.CharField(max_length=100)
    sort = models.IntegerField()
    created_at = models.DateTimeField()
    menu_id = models.IntegerField()
    urls = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'superadmin_submenu'


class ExternalAccessMenu(models.Model):
    role_id = models.IntegerField()
    menu_id = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'superadmin_accessmenu'

        

class PresenceLog(models.Model):
    TYPE_CHOICES = (
        ('in', 'Masuk'),
        ('out', 'Pulang'),
    )
    email = models.EmailField()
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='absen_photos/', null=True, blank=True)
    type = models.CharField(max_length=5, choices=TYPE_CHOICES, default='in')  # << tambah ini

    class Meta:
        db_table = 'presence_log'

class TrainingFace(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    encoding = models.BinaryField()  # Simpan encoding wajah
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    class Meta:
        db_table = 'training_face'
