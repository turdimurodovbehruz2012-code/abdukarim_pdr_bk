# config/urls.py
from django.contrib import admin
from django.urls import path
from counter import views

urlpatterns = [
    path('', views.login_page),
    path('api/track/', views.track),
    path('api/stats/', views.statistics),
    path('api/admin/login/', views.admin_login),
    path('api/admin/stats/', views.admin_stats),
    path('api/admin/logout/', views.admin_logout),
]