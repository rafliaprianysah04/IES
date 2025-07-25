from django.db import connection
from django.urls import reverse, NoReverseMatch

def resolve_url_path(url_str):
    try:
        return reverse(url_str)
    except NoReverseMatch:
        return url_str or '#'

def token_context(request):
    return {'token': request.GET.get('token', '')}

def menu_context(request):
    user = getattr(request, 'user', None)

    if not user or not hasattr(user, 'role_id') or not hasattr(user, 'app_id'):
        print("[DEBUG] Context: Tidak ada user atau user tidak valid.")
        return {'menu_with_subs': []}

    role_id = user.role_id
    app_id_user = user.app_id
    current_app_id = getattr(request.resolver_match, 'app_name', app_id_user)

    menu_with_subs = []

    with connection.cursor() as cursor:
        if app_id_user == 'superadmin':
            print(f"[DEBUG] Superadmin mode: ambil menu dari app_id = {current_app_id}")
            cursor.execute("""
                SELECT DISTINCT m.id, m.nama_menu, m.icon_menu, m.sort, m.app_id
                FROM superadmin_menu m
                INNER JOIN superadmin_accessmenu am ON m.id = am.menu_id
                WHERE m.is_active = TRUE
                  AND m.app_id = %s
                  AND am.role_id = %s
                ORDER BY m.sort ASC
            """, [current_app_id, role_id])
        else:
            cursor.execute("""
                SELECT DISTINCT m.id, m.nama_menu, m.icon_menu, m.sort, m.app_id
                FROM superadmin_menu m
                INNER JOIN superadmin_accessmenu am ON m.id = am.menu_id
                WHERE m.is_active = TRUE
                  AND m.app_id = %s
                  AND am.role_id = %s
                ORDER BY m.sort ASC
            """, [app_id_user, role_id])

        menus_raw = cursor.fetchall()
        print(f"[DEBUG] Jumlah menu ditemukan: {len(menus_raw)}")

        for menu_id, nama_menu, icon_menu, sort, app_id in menus_raw:
            # Ambil submenu untuk menu ini dan app_id yang sama
            cursor.execute("""
                SELECT sm.id, sm.urls, sm.icon_submenu, sm.nama_submenu
                FROM superadmin_submenu sm
                INNER JOIN superadmin_menu m ON sm.menu_id = m.id
                INNER JOIN superadmin_accessmenu am ON m.id = am.menu_id
                WHERE sm.menu_id = %s
                  AND m.app_id = %s
                  AND m.is_active = TRUE
                  AND am.role_id = %s
                ORDER BY sm.sort ASC
            """, [menu_id, app_id, role_id])

            submenus = cursor.fetchall()

            submenu_objs = [
                {
                    'id': sid,
                    'url': resolve_url_path(urls),
                    'icon': icon,
                    'name': nama_sub
                }
                for sid, urls, icon, nama_sub in submenus
            ]

            menu_with_subs.append({
                'id': menu_id,
                'name': nama_menu,
                'icon': icon_menu,
                'app_id': app_id,
                'submenus': submenu_objs
            })

    print(f"[DEBUG] Final menu_with_subs: {menu_with_subs}")
    return {'menu_with_subs': menu_with_subs}
