from django.urls import path
from . import views

app_name = 'operator_stack'

urlpatterns = [

    path('dashboard/', views.dashboard_operator, name='dashboard_operator'),
    path('shifting/', views.shifting, name='shifting'),
    path('denah/', views.denah_storage, name='denah_storage'),
    path('stacking/', views.stacking_view, name='stacking_in'),
]