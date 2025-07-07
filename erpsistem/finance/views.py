from django.shortcuts import render
from django.urls import reverse, NoReverseMatch
from .utils import get_user_from_token
from .models import ExternalMenu, ExternalAccessMenu, ExternalSubMenu

def resolve_url_path(url_str):
    try:
        return reverse(url_str)
    except NoReverseMatch:
        return '#'  # fallback jika nama route tidak ditemukan

def dashboard(request):
    # Ambil token dari query parameter
    token = request.GET.get('token', '')

    # Ambil user dari token
    user = get_user_from_token(request)

    if not user:
        return render(request, 'finance/unauthorized.html', status=401)

    app_id = user.app_id
    role_id = user.role_id

    # Ambil menu yang sesuai
    menu_ids = ExternalAccessMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)

    menus = ExternalMenu.objects.filter(
        app_id=app_id,
        is_active=True,
        id__in=menu_ids
    ).order_by('sort')

    data = []
    for menu in menus:
        # Resolve URL menu jika ada field 'url' di model ExternalMenu, jika tidak ada pakai '#'
        menu_url = getattr(menu, 'url', None)
        menu_url_resolved = resolve_url_path(menu_url) if menu_url else '#'

        submenus = ExternalSubMenu.objects.filter(menu_id=menu.id).order_by('sort')
        submenu_list = []
        for submenu in submenus:
            url_resolved = resolve_url_path(submenu.urls)
            submenu_list.append({
                'id': submenu.id,
                'name': submenu.nama_submenu,
                'icon': submenu.icon_submenu,
                'url': url_resolved,
            })

        data.append({
            'id': menu.id,
            'name': menu.nama_menu,
            'icon': menu.icon_menu,
            'url': menu_url_resolved,
            'submenus': submenu_list,
        })

    return render(request, 'finance/dashboard.html', {
        'user': user,
        'menu_with_subs': data,
        'token': token,
    })

def coa(request):
    # Ambil token dari query parameter
    token = request.GET.get('token', '')

    # Ambil user dari token
    user = get_user_from_token(request)

    if not user:
        return render(request, 'finance/unauthorized.html', status=401)

    app_id = user.app_id
    role_id = user.role_id

    # Ambil menu yang sesuai
    menu_ids = ExternalAccessMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)

    menus = ExternalMenu.objects.filter(
        app_id=app_id,
        is_active=True,
        id__in=menu_ids
    ).order_by('sort')

    data = []
    for menu in menus:
        # Resolve URL menu jika ada field 'url' di model ExternalMenu, jika tidak ada pakai '#'
        menu_url = getattr(menu, 'url', None)
        menu_url_resolved = resolve_url_path(menu_url) if menu_url else '#'

        submenus = ExternalSubMenu.objects.filter(menu_id=menu.id).order_by('sort')
        submenu_list = []
        for submenu in submenus:
            url_resolved = resolve_url_path(submenu.urls)
            submenu_list.append({
                'id': submenu.id,
                'name': submenu.nama_submenu,
                'icon': submenu.icon_submenu,
                'url': url_resolved,
            })

        data.append({
            'id': menu.id,
            'name': menu.nama_menu,
            'icon': menu.icon_menu,
            'url': menu_url_resolved,
            'submenus': submenu_list,
        })

    return render(request, 'finance/coa.html', {
        'user': user,
        'menu_with_subs': data,
        'token': token,
    })
