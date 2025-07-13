from django.urls import path
from . import views

app_name = 'app_partition'

urlpatterns = [
    path('', views.app_view, name='app_view'),
    # path('logout/', views.logout_view, name='logout'),  # boleh aktifkan nanti kalau perlu
]
