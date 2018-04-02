from django.db import models

class Administrator (models.Model):
    userName = models.CharField(max_length=45)
    password = models.CharField(max_length=64)
    pw2 = models.CharField(max_length=45)
    email = models.CharField(max_length=100)


    class Meta:
        db_table = "administrator"