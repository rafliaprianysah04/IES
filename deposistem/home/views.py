from django.shortcuts import render
from datetime import datetime
from django.urls import reverse
from .utils import *

def home(request):
    user = get_user_from_token(request)
    if not user:
        return render(request, 'unauthorized.html', status=401)

    # Ambil token dari URL agar bisa disisipkan kembali
    token = request.GET.get('token', '')

    menus = [
        {
            'name': 'Surveyor',
            'icon': 'fa-wallet',
            'color': '#27ae60',
            'url': reverse('surveyor:dashboard') + f'?token={token}',
        },
        {
            'name': 'Operator',
            'icon': 'fa-wifi',
            'color': '#2980b9',
            'url': reverse('operator_stack:dashboard_operator') + f'?token={token}',
        },
        {
            'name': 'Customer Service',
            'icon': 'fa-users',
            'color': '#e67e22',
            'url': '/hris/',
        },
        {
            'name': 'MNR',
            'icon': 'fa-graduation-cap',
            'color': '#8e44ad',
            'url': '/lms/',
        },
        {
            'name': 'Security',
            'icon': 'fa-graduation-cap',
            'color': '#8e44ad',
            'url': '/lms/',
        },
        {
            'name': 'Tax',
            'icon': 'fa-graduation-cap',
            'color': '#8e44ad',
            'url': '/lms/',
        },
    ]
    return render(request, 'dashboard.html', {
        'menus': menus,
        'now': datetime.now(),
    })
