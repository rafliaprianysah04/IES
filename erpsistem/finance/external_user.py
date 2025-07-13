from django.db import models

class ExternalUser(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(db_column='first_name', max_length=150)
    last_name = models.CharField(db_column='last_name',max_length=150)
    username = models.CharField(max_length=150)
    email = models.EmailField()
    role_id = models.IntegerField()
    app_id = models.CharField(max_length=100)
    

    class Meta:

        db_table = 'login_user'

    @property
    def is_authenticated(self):
        return True
