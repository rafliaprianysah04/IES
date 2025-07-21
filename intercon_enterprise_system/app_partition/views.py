from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken

from login.models import User
from superadmin.models import Role

@login_required
@login_required
def app_view(request):
    user = request.user

    # Gunakan app_id langsung sebagai penentu role_name
    role_name = (user.app_id or '').lower().strip()

    # Buat token JWT untuk user saat ini
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    # URL dengan token
    finance_url = f"http://127.0.0.1:8888/finance/?token={token}"
    online_presence = f"http://127.0.0.1:8118/presence/?token={token}"
    depo_url = f"http://127.0.0.1:8883/home/?token={token}"

    base_menus = {
        'finance': [
            {
                'name': 'Finance',
                'icon': 'fa-wallet',
                'color': '#27ae60',
                'url': finance_url,
            },
            {
                'name': 'Online Presence',
                'icon': 'fa-wifi',
                'color': '#2980b9',
                'url': online_presence,
            },
            {
                'name': 'Learning Management System',
                'icon': 'fa-graduation-cap',
                'color': '#8e44ad',
                'url': '/lms/',
            },
        ],
        'security': [
            {
                'name': 'Depo Management System',
                'icon': 'fa-file-invoice-dollar',
                'color': '#34495e',
                'url': depo_url,
            },
            {
                'name': 'Online Presence',
                'icon': 'fa-wifi',
                'color': '#2980b9',
                'url': online_presence,
            },
            {
                'name': 'Learning Management System',
                'icon': 'fa-graduation-cap',
                'color': '#8e44ad',
                'url': '/lms/',
            },
        ],
        'superadmin': [
            {
                'name': 'Superadmin',
                'icon': 'fa-shield-alt',
                'color': '#2ecc71',
                'url': '/superadmin/',
            },
            {
                'name': 'Depo System',
                'icon': 'fa-file-invoice-dollar',
                'color': '#34495e',
                'url': depo_url,
            },
            {
                'name': 'Finance',
                'icon': 'fa-wallet',
                'color': '#27ae60',
                'url': finance_url,
            },
            {
                'name': 'Hris',
                'icon': 'fa-users',
                'color': '#e67e22',
                'url': '/hris/',
            },
            {
                'name': 'Online Presence',
                'icon': 'fa-wifi',
                'color': '#2980b9',
                'url': online_presence,
            },
            {
                'name': 'Learning Management System',
                'icon': 'fa-graduation-cap',
                'color': '#8e44ad',
                'url': '/lms/',
            },
            {
                'name': 'Portal Customer',
                'icon': 'fa-graduation-cap',
                'color': '#8e44ad',
                'url': '/lms/',
            },
        ]
    }

    menus = base_menus.get(role_name, [])

    return render(request, 'app_partition/app_view.html', {
        'menus': menus,
        'now': datetime.now(),
        'role_name': role_name,
    })
