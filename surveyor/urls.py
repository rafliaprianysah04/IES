from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = 'surveyor'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('container-in/', views.container_in_view, name='container_in'),
    path('container-in/list', views.container_in_list_view, name='container_in_list'),
    path('check-container/', views.cek_valid_container, name='cek_valid_container'),
    path(
        'container-in/photos/<str:referal>/<str:container_no>/',
        views.container_photo_gallery,
        name='container_photos'
    ),
    path(
        'container-in/photos/pdf/<str:referal>/<str:container_no>/',
        views.download_container_photos_pdf,
        name='download_container_photos_pdf'
    ),
    path('upload-rooftop/', views.upload_rooftop_view, name='upload_rooftop'),
    path('upload-rooftop/ajax/', views.upload_rooftop_photo, name='upload_rooftop_photo'),
    path('upload-under/', views.upload_under_view, name='upload_under'),
    path('upload-under/ajax/', views.upload_under_photo, name='upload_under_photo'),
    path('shifting/', views.shifting_view, name='shifting'),
    path('verify-container/', views.verify_container_exists, name='verify_container_exists'),
    path('get-container-photos/ajax', views.get_container_photos, name='get_container_photos'),
    path('save-container/', views.save_container_ajax, name='save_container_ajax'),
    
    # ✅ Tambahkan endpoint ini
    path('save-placement/ajax', views.simpan_penempatan_container, name='simpan_penempatan_container'),
]
