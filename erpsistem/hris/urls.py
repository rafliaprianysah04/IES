from django.urls import path
from . import views

app_name = 'hris'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
