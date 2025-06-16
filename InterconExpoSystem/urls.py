from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('system_login.urls', namespace='login_sistem')),
    path('consignee/', include('consignee.urls', namespace='consignee')),
    path('customer_service/', include('customer_service.urls', namespace='customer_service')),
    path('surveyor/', include('surveyor.urls', namespace='surveyor')),
    path('gateinout/', include('gate_in_out.urls', namespace='gateinout')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
