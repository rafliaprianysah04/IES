from django.db import models

# Create your models here.
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