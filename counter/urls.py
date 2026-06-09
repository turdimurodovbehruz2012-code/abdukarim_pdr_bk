# config/urls.py
from django.contrib import admin
from django.urls import path
from counter import views
from django.http import JsonResponse

def home(request):
    return JsonResponse({'message': 'API ishlayapti'})

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/statistics/', views.stats),
    path('api/track/', views.track_visit),
    path('api/check-password/', views.verify_statistic_password),
    path('api/statistic-admin/', views.statistic_admin_session),
    path('api/statistic-logout/', views.statistic_logout),
    path('statistic_admin/', views.statistic_admin),
]