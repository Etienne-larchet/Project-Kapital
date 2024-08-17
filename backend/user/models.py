from django.db import models


class Connection(models.Model):
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=40)
    new_user = models.BooleanField()
