# counter/models.py
from django.db import models

class Visitor(models.Model):
    ip = models.GenericIPAddressField(unique=True)
    country = models.CharField(max_length=100, default='Unknown')
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

class TotalRequest(models.Model):
    count = models.IntegerField(default=0)