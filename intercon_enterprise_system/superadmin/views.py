from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from .models import Role, Menu, SubMenu, AccessMenu
from login.models import User  # Custom User model from app login
from django.views.decorators.csrf import csrf_exempt
import json

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

# Superadmin access check
def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role_id == 1 and request.user.app_id == 'superadmin':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('Access Denied: Anda bukan superadmin.')
    return wrapper

@login_required
@superadmin_required
def dashboard(request):
    context = {
        'user_count': User.objects.count(),
        'role_count': Role.objects.count(),
        'menu_count': Menu.objects.count(),
        'submenu_count': SubMenu.objects.count(),
    }
    return render(request, 'superadmin/dashboard.html', context)

@login_required
@superadmin_required
def user_view(request):
    roles = Role.objects.filter(is_active=True)
    users = User.objects.all()
    return render(request, 'superadmin/user.html', {'roles': roles, 'users': users})

@login_required
@superadmin_required
def role_view(request):
    roles = Role.objects.all()
    return render(request, 'superadmin/role.html', {'roles': roles})

@login_required
@superadmin_required
def menu_view(request):
    menus = Menu.objects.all()
    return render(request, 'superadmin/menu.html', {'menus': menus})

@login_required
@superadmin_required
def submenu_view(request):
    submenus = SubMenu.objects.select_related('menu').all()
    menus = Menu.objects.all()
    return render(request, 'superadmin/submenu.html', {'submenus': submenus, 'menus': menus})

@login_required
@superadmin_required
def access_menu_view(request):
    access = AccessMenu.objects.select_related('role', 'menu').all()
    roles = Role.objects.all()
    menus = Menu.objects.all()
    return render(request, 'superadmin/access_menu.html', {'access': access, 'roles': roles, 'menus': menus})

@login_required
def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login:logout')

# API: ROLE
@csrf_exempt
@login_required
@superadmin_required
def role_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        nama = data.get('nama_role')
        is_active = data.get('is_active', True)

        if id:
            role = get_object_or_404(Role, id=id)
            role.nama_role = nama
            role.is_active = is_active
            role.save()
            return JsonResponse({'status': 'updated'})
        else:
            if Role.objects.filter(nama_role=nama).exists():
                return JsonResponse({'status': 'exists'})
            Role.objects.create(nama_role=nama, is_active=is_active)
            return JsonResponse({'status': 'created'})

    elif request.method == 'DELETE':
        data = json.loads(request.body)
        id = data.get('id')
        Role.objects.filter(id=id).delete()
        return JsonResponse({'status': 'deleted'})

    elif request.method == 'GET':
        roles = list(Role.objects.values())
        return JsonResponse({'data': roles})

# API: USER
@csrf_exempt
@login_required
@superadmin_required
@csrf_exempt
def user_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        id = data.get('id')
        username = data.get('username')
        email = data.get('email')
        role_id = data.get('role_id')
        is_active = data.get('is_active', True)
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        app_id = data.get('app_id', '')

        if id:
            # Update user yang sudah ada
            user = get_object_or_404(User, id=id)
            user.username = username
            user.email = email
            user.role_id = role_id
            user.is_active = is_active
            user.first_name = first_name
            user.last_name = last_name
            user.app_id = app_id
            user.save()
            return JsonResponse({'status': 'updated'})
        else:
            # Cek apakah username sudah ada
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'exists'})

            # Buat user baru dengan password default 'Intercon1'
            user = User(
                username=username,
                email=email,
                role_id=role_id,
                is_active=is_active,
                first_name=first_name,
                last_name=last_name,
                app_id=app_id
            )
            user.set_password('Intercon1')
            user.save()
            return JsonResponse({'status': 'created'})

    elif request.method == 'PATCH':
        data = json.loads(request.body)
        id = data.get('id')
        is_active = data.get('is_active')

        if id is None or is_active is None:
            return JsonResponse({'status': 'error', 'message': 'ID dan status harus disertakan'}, status=400)

        try:
            user = User.objects.get(id=id)
            user.is_active = is_active
            user.save()
            return JsonResponse({'status': 'updated'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User tidak ditemukan'}, status=404)

    elif request.method == 'DELETE':
        data = json.loads(request.body)
        id = data.get('id')
        User.objects.filter(id=id).delete()
        return JsonResponse({'status': 'deleted'})

    elif request.method == 'GET':
        users = list(User.objects.values())
        return JsonResponse({'data': users})

# API: MENU
@csrf_exempt
@login_required
@superadmin_required
def menu_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        nama_menu = data.get('nama_menu')
        icon_menu = data.get('icon_menu')
        app_id = data.get('app_id', 'intercon_enterprise_system')
        sort = data.get('sort')

        is_active = data.get('is_active', True)
        if id:
            menu = get_object_or_404(Menu, id=id)
            menu.nama_menu = nama_menu
            menu.icon_menu = icon_menu
            menu.app_id = app_id
            menu.sort = sort
            menu.is_active = is_active
            menu.save()
            return JsonResponse({'status': 'updated'})
        else:
            if Menu.objects.filter(nama_menu=nama_menu).exists():
                return JsonResponse({'status': 'exists'})
            Menu.objects.create(nama_menu=nama_menu, icon_menu=icon_menu, app_id=app_id, sort=sort, is_active=is_active)
            return JsonResponse({'status': 'created'})
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        id = data.get('id')
        Menu.objects.filter(id=id).delete()
        return JsonResponse({'status': 'deleted'})
    elif request.method == 'GET':
        menus = list(Menu.objects.values())
        return JsonResponse({'data': menus})

# API: SUBMENU
@csrf_exempt
@login_required
@superadmin_required
def submenu_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        menu_id = data.get('menu_id')
        name_submenu = data.get('name_submenu')  # Pastikan JS mengirim "name_submenu"
        urls = data.get('urls')
        icon = data.get('icon_submenu')
        sort = data.get('sort', 0)

        if not all([menu_id, name_submenu, urls]):
            return JsonResponse({'status': 'error', 'message': 'Data tidak lengkap.'})

        if id:
            submenu = get_object_or_404(SubMenu, id=id)
            submenu.name_submenu = name_submenu
            submenu.menu_id = menu_id
            submenu.urls = urls
            submenu.icon_submenu = icon
            submenu.sort = sort
            submenu.save()
            return JsonResponse({'status': 'updated'})
        else:
            SubMenu.objects.create(
                menu_id=menu_id,
                nama_submenu=name_submenu,
                urls=urls,
                icon_submenu=icon,
                sort=sort
            )
            return JsonResponse({'status': 'created'})

    elif request.method == 'DELETE':
        data = json.loads(request.body)
        id = data.get('id')
        SubMenu.objects.filter(id=id).delete()
        return JsonResponse({'status': 'deleted'})

    elif request.method == 'GET':
        submenus = list(SubMenu.objects.values())
        return JsonResponse({'data': submenus})

# API: ACCESS MENU
@csrf_exempt
@login_required
@superadmin_required
def access_menu_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        role_id = data.get('role_id')
        menu_id = data.get('menu_id')
        if id:
            access = get_object_or_404(AccessMenu, id=id)
            access.role_id = role_id
            access.menu_id = menu_id
            access.save()
            return JsonResponse({'status': 'updated'})
        else:
            AccessMenu.objects.create(role_id=role_id, menu_id=menu_id)
            return JsonResponse({'status': 'created'})
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        id = data.get('id')
        AccessMenu.objects.filter(id=id).delete()
        return JsonResponse({'status': 'deleted'})
    elif request.method == 'GET':
        access = list(AccessMenu.objects.values())
        return JsonResponse({'data': access})
