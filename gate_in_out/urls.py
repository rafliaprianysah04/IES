from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = 'gate_in_out'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('truck-in/', views.truck_in, name='truck_in'),
    path('truck-out/', views.truck_out, name='truck_out'),
]
