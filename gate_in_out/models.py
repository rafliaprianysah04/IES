from django.db import models

# Create your models here.

class GateIn(models.Model):
    eir_in = models.DateField()  # date
    truck_no = models.CharField(max_length=15)  # varchar 15 character
    trucking_name = models.CharField(max_length=100)  # varchar 100 character
    path_foto = models.TextField()  # text
    created_by = models.CharField(max_length=50)  # text
    created_at = models.DateTimeField(auto_now_add=True)  # date
    updated_at = models.DateTimeField(auto_now=True)  # date

    def __str__(self):
        return f'{self.truck_no} - {self.trucking_name}'

    class Meta:
        verbose_name = "Gate In"
        verbose_name_plural = "Gate Ins"
        ordering = ['-created_at']


class GateOut(models.Model):
    eir_out = models.DateField()  # date
    foto_container = models.TextField()  # tambahan field: text
    no_container = models.CharField(max_length=20)  # tambahan field: varchar 20 character
    truck_no = models.CharField(max_length=15)  # varchar 15 character
    trucking_name = models.CharField(max_length=100)  # varchar 100 character
    path_foto = models.TextField()  # text
    created_by = models.CharField(max_length=50)  # text
    created_at = models.DateTimeField(auto_now_add=True)  # date
    updated_at = models.DateTimeField(auto_now=True)  # date

    def __str__(self):
        return f'{self.no_container} - {self.truck_no} - {self.trucking_name}'

    class Meta:
        verbose_name = "Gate Out"
        verbose_name_plural = "Gate Outs"
        ordering = ['-created_at']
