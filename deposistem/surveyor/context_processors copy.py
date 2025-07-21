from django.db import connection
from django.urls import reverse, NoReverseMatch

def resolve_url_path(url_str):
    try:
        return reverse(url_str)
    except NoReverseMatch:
        return '#'  # fallback jika error

def menu_context(request):
    if request.user.is_authenticated:
        role_id = request.user.role_id
        app_id = request.user.app_id

        with connection.cursor() as cursor:
            # Superadmin: ambil semua menu dari semua app yang role-nya punya akses
            if app_id == 'superadmin':
                cursor.execute("""
                    SELECT DISTINCT m.id, m.nama_menu, m.icon_menu, m.sort
                    FROM superadmin_menu m
                    INNER JOIN superadmin_accessmenu am ON m.id = am.menu_id
                    WHERE m.is_active = TRUE
                      AND am.role_id = %s
                    ORDER BY m.sort ASC
                """, [role_id])
            else:
                # Role biasa: filter berdasarkan app_id
                cursor.execute("""
                    SELECT DISTINCT m.id, m.nama_menu, m.icon_menu, m.sort
                    FROM superadmin_menu m
                    INNER JOIN superadmin_accessmenu am ON m.id = am.menu_id
                    WHERE m.is_active = TRUE
                      AND m.app_id = %s
                      AND am.role_id = %s
                    ORDER BY m.sort ASC
                """, [app_id, role_id])

            menus_raw = cursor.fetchall()
            print("User:", request.user)
            print("App ID:", app_id)
            print("Role ID:", role_id)
            print("Menu fetched:", menus_raw)

            menu_with_subs = []

            for menu_id, nama_menu, icon_menu, sort in menus_raw:
                cursor.execute("""
                    SELECT id, urls, icon_submenu, nama_submenu
                    FROM superadmin_submenu
                    WHERE menu_id = %s
                    ORDER BY sort ASC
                """, [menu_id])
                submenus = cursor.fetchall()

                print(f"Menu ID {menu_id} has {len(submenus)} submenu(s)")

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
                    'submenus': submenu_objs
                })

            print("Final menu_with_subs:", menu_with_subs)

        return {'menu_with_subs': menu_with_subs}

    return {'menu_with_subs': []}
