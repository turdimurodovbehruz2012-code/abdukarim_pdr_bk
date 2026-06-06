# admin.py
from django.contrib import admin
from .models import Visitor, TotalRequest
from django.contrib.admin import SimpleListFilter

class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip', 'country', 'first_seen', 'last_seen')
    list_filter = ('country', 'first_seen')
    search_fields = ('ip', 'country')
    readonly_fields = ('ip', 'country', 'first_seen', 'last_seen')

class TotalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'count')
    readonly_fields = ('count',)

admin.site.register(Visitor, VisitorAdmin)
admin.site.register(TotalRequest, TotalRequestAdmin)