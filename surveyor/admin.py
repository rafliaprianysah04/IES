from django.contrib import admin
from .models import SurveyInContainer

@admin.register(SurveyInContainer)
class ContainerAdmin(admin.ModelAdmin):
    fields = [
        'container_no', 'customer_code', 'container_type', 'size', 'condition',
        'washing', 'grade', 'act_in', 'manufacture', 'tare', 'payload',
        'haulier', 'truck', 'washing_by', 'remark', 'created_at'
    ]
    readonly_fields = ['created_at']
