from django.db import connection
from django.urls import reverse, NoReverseMatch

def resolve_url_path(url_str):
    try:
        return reverse(url_str)
    except NoReverseMatch:
        return '#'  # fallback jika error

def token_context(request):
    return {'token': request.GET.get('token', '')}

def menu_context(request):
    if request.user.is_authenticated:
        role_id = request.user.role_id
        app_id = request.user.app_id

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT m.id, m.nama_menu, m.icon_menu, m.sort
                FROM superadmin_menu m
                INNER JOIN superadmin_accessmenu am ON m.id = am.menu_id
                WHERE m.is_active = TRUE AND m.app_id = %s AND am.role_id = %s
                ORDER BY m.sort ASC
            """, [app_id, role_id])
            menus_raw = cursor.fetchall()

            menu_with_subs = []

            for menu_id, nama_menu, icon_menu, sort in menus_raw:
                cursor.execute("""
                    SELECT id, urls, icon_submenu, nama_submenu
                    FROM superadmin_submenu
                    WHERE menu_id = %s
                    ORDER BY sort ASC
                """, [menu_id])
                submenus = cursor.fetchall()

                submenu_objs = [
                    {
                        'id': sid,
                        'url': resolve_url_path(urls),
                        'icon': icon,
                        'name': nama_sub  # ubah jadi 'name' supaya konsisten dengan template
                    }
                    for sid, urls, icon, nama_sub in submenus
                ]

                menu_with_subs.append({
                    'id': menu_id,
                    'name': nama_menu,     # ubah juga jadi 'name'
                    'icon': icon_menu,
                    'submenus': submenu_objs
                })

        return {'menu_with_subs': menu_with_subs}

    return {'menu_with_subs': []}
