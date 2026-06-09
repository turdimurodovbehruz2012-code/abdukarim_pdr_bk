
from django.db import models

class Visitor(models.Model):
    ip = models.GenericIPAddressField(unique=True)
    country = models.CharField(max_length=100, default='Unknown')
    first_seen = models.DateTimeField(auto_now_add=True)

class TotalRequest(models.Model):
    count = models.IntegerField(default=0)

class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)