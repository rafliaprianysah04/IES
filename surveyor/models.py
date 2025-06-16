from django.db import models

class SurveyInContainer(models.Model):
    container_no = models.CharField(max_length=11, unique=True)
    referal = models.CharField(max_length=10, unique=True, null=True, blank=True)

    customer_code = models.CharField(max_length=10)
    container_type = models.CharField(max_length=5)
    size = models.CharField(max_length=5)
    condition = models.CharField(max_length=5)
    washing = models.CharField(max_length=5)
    grade = models.CharField(max_length=2)
    act_in = models.CharField(max_length=5)
    manufacture = models.CharField(max_length=7, null=True, blank=True)  # Format: YYYY-MM
    tare = models.CharField(max_length=20, null=True, blank=True)
    payload = models.CharField(max_length=20, null=True, blank=True)
    haulier = models.CharField(max_length=20, null=True, blank=True)
    truck = models.CharField(max_length=20, null=True, blank=True)

    washing_by = models.CharField(max_length=50, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.container_no

class MappingContainer(models.Model):
    container_no = models.CharField(max_length=20, null=True, blank=True)
    block = models.CharField(max_length=5)
    spec = models.CharField(max_length=5)
    row = models.CharField(max_length=5)
    tier = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('block', 'spec', 'row', 'tier')

    def __str__(self):
        return f'{self.container_no or "-"} @ {self.block}-{self.spec}-{self.row}-{self.tier}'
