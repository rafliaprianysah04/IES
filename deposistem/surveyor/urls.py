from django.urls import path
from . import views

app_name = 'surveyor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('input_surveyin/', views.surveyin, name='surveyin'),
    path('list_surveyin/', views.list_surveyin, name='list_surveyin'),
    path('view_surveyin/<int:id>/', views.view_surveyin, name='view_surveyin'),
    path('get_container_qrcode/', views.get_container_qrcode, name='get_container_qrcode'),
    
]
