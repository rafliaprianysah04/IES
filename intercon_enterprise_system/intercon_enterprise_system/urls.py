# intercon_enterprise_system/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('login.urls', namespace='login')),
    path('app/', include('app_partition.urls', namespace='app_partition')), # Tambahkan ini
    path('superadmin/', include('superadmin.urls', namespace='superadmin')), # Tambahkan ini
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]