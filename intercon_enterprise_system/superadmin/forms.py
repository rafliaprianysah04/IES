# superadmin/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Role, Menu, Submenu, AccessMenu

User = get_user_model() # Mengambil model User kustom

# Custom widget untuk switch-like radio button
class BootstrapSwitchInput(forms.RadioSelect):
    template_name = 'superadmin/widgets/bootstrap_switch.html'
    option_template_name = 'superadmin/widgets/bootstrap_switch_option.html'

class UserForm(forms.ModelForm):
    """
    Formulir untuk manajemen User.
    Menyesuaikan input password dan is_active.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False, # Password tidak wajib saat update, hanya saat create atau jika diubah
        help_text="Biarkan kosong jika tidak ingin mengubah password."
    )
    # Override field role untuk menggunakan ModelChoiceField
    role = forms.ModelChoiceField(
        queryset=Role.objects.all().order_by('nama_role'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Peran"
    )
    # Menggunakan custom widget untuk is_active
    is_active = forms.BooleanField(
        widget=BootstrapSwitchInput(choices=[(True, 'Aktif'), (False, 'Tidak Aktif')]),
        required=False,
        initial=True, # Default aktif
        label="Status Akun"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # Password widget sudah di-override di atas
            # role widget sudah di-override di atas
            # is_active widget sudah di-override di atas
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Jika instance sudah ada (mode edit), hapus password dari initial data
        if self.instance.pk:
            self.fields['password'].initial = "" # Jangan tampilkan password hash di form edit

        # Pastikan is_active memiliki nilai yang benar untuk BootstrapSwitchInput
        # Jika instance.is_active adalah True, initial akan jadi True, dan begitu pula sebaliknya
        if self.instance.pk:
            self.fields['is_active'].initial = self.instance.is_active
        else:
            self.fields['is_active'].initial = True # Default true for new users


    def save(self, commit=True):
        user = super().save(commit=False)
        # Handle password
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class RoleForm(forms.ModelForm):
    """
    Formulir untuk manajemen Role.
    """
    is_active = forms.BooleanField(
        widget=BootstrapSwitchInput(choices=[(True, 'Aktif'), (False, 'Tidak Aktif')]),
        required=False,
        initial=True, # Default aktif
        label="Status Peran"
    )
    class Meta:
        model = Role
        fields = ['nama_role', 'is_active']
        widgets = {
            'nama_role': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['is_active'].initial = self.instance.is_active
        else:
            self.fields['is_active'].initial = True

class MenuForm(forms.ModelForm):
    """
    Formulir untuk manajemen Menu.
    """
    is_active = forms.BooleanField(
        widget=BootstrapSwitchInput(choices=[(True, 'Aktif'), (False, 'Tidak Aktif')]),
        required=False,
        initial=True, # Default aktif
        label="Status Menu"
    )
    class Meta:
        model = Menu
        fields = ['nama_menu', 'icon_menu', 'is_active', 'sort']
        widgets = {
            'nama_menu': forms.TextInput(attrs={'class': 'form-control'}),
            'icon_menu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: fas fa-home'}),
            'sort': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['is_active'].initial = self.instance.is_active
        else:
            self.fields['is_active'].initial = True

class SubmenuForm(forms.ModelForm):
    """
    Formulir untuk manajemen Submenu.
    """
    menu = forms.ModelChoiceField(
        queryset=Menu.objects.all().order_by('nama_menu'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Menu Utama"
    )
    is_active = forms.BooleanField(
        widget=BootstrapSwitchInput(choices=[(True, 'Aktif'), (False, 'Tidak Aktif')]),
        required=False,
        initial=True, # Default aktif
        label="Status Submenu"
    )
    class Meta:
        model = Submenu
        fields = ['menu', 'nama_submenu', 'urls', 'icon_submenu', 'is_active', 'sort']
        widgets = {
            'nama_submenu': forms.TextInput(attrs={'class': 'form-control'}),
            'urls': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: /superadmin/users/'}),
            'icon_submenu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: fas fa-users'}),
            'sort': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['is_active'].initial = self.instance.is_active
        else:
            self.fields['is_active'].initial = True

class AccessMenuForm(forms.ModelForm):
    """
    Formulir untuk manajemen AccessMenu.
    """
    role = forms.ModelChoiceField(
        queryset=Role.objects.all().order_by('nama_role'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Peran"
    )
    menu = forms.ModelChoiceField(
        queryset=Menu.objects.all().order_by('nama_menu'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Menu"
    )
    class Meta:
        model = AccessMenu
        fields = ['role', 'menu']
        # id_data tidak perlu di sini karena itu primary key AutoField

