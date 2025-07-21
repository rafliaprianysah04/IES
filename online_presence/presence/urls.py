from django.urls import path
from . import views

app_name = 'presence'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('absen/', views.absen_view, name='presence'),
    path('recognize/', views.recognize_and_log, name='recognize_and_log'),
    path('dataset/', views.train_view, name='dataset'),
    path('training_face/', views.train_face, name='train_face'),
] 