from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = 'consignee'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('import/', views.import_view, name='import'),
    path('export/', views.dashboard_view, name='export'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/detail/<str:reservasi_id>/', views.reservasi_detail_view, name='reservasi_detail'),

    # Function
    path('simpan-reservasi-db/', views.simpan_reservasi_db, name='simpan_reservasi_db'),
]
