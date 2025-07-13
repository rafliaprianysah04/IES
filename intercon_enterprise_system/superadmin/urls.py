from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('user/', views.user_view, name='user'),
    path('role/', views.role_view, name='role'),
    path('menu/', views.menu_view, name='menu'),
    path('submenu/', views.submenu_view, name='submenu'),
    path('access_menu/', views.access_menu_view, name='access_menu'),
    path('logout/', views.logout_view, name='logout'),

    # API AJAX Routes
    path('api/user/', views.user_api, name='user_api'),
    path('api/role/', views.role_api, name='role_api'),
    path('api/menu/', views.menu_api, name='menu_api'),
    path('api/submenu/', views.submenu_api, name='submenu_api'),
    path('api/access_menu/', views.access_menu_api, name='access_menu_api'),
]

handler404 = 'superadmin.urls.custom_404'