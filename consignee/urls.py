from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = 'consignee'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('import/', views.import_view, name='import'),
    path('keranjang/', views.keranjang, name='keranjang'), #Dimas (17-06-2025)
    #path('export/', views.export_view, name='export'),
    path('export/', views.container_export, name='export'), #Dimas (17-06-2025)
    path('export/detail_export/<int:id>/', views.detail_export, name='detail_export'), #Dimas (17-06-2025)
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/detail/<str:reservasi_id>/', views.reservasi_detail_view, name='reservasi_detail'),

    # Function
    path('simpan-reservasi-db/', views.simpan_reservasi_db, name='simpan_reservasi_db'),
]
