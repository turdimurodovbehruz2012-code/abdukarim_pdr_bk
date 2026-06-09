# counter/admin.py
from django.contrib import admin
from .models import Visitor, TotalRequest

admin.site.register(Visitor)
admin.site.register(TotalRequest)
