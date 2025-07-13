from django.db import models

class Role(models.Model):
    nama_role = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_role

class Menu(models.Model):
    nama_menu = models.CharField(max_length=100)
    icon_menu = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    sort = models.IntegerField()
    app_id = models.CharField(max_length=50, default='intercon_enterprise_system')  # kolom baru
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_menu

class SubMenu(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    nama_submenu = models.CharField(max_length=100, default='Submenu')
    urls = models.CharField(max_length=200)
    icon_submenu = models.CharField(max_length=100, blank=True)
    sort = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.menu.nama_submenu} - {self.urls}"

class AccessMenu(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role.nama_role} akses {self.menu.nama_menu}"