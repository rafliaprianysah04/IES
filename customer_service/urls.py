from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = 'customer_service'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('approve_reservasi/', views.approve_reservasi_view, name='approve_reservasi'),

    # Function# urls.py
    path('approve_reservasi/detail/<str:reservasi_id>/', views.reservasi_detail_view, name='reservasi_detail'),
    path('approve_reservasi/<str:reservasi_id>/', views.approve_reservasi_done, name='approve_reservasi_done'),
]
