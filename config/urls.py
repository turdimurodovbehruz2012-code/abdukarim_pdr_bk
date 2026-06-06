from django.contrib import admin
from django.urls import path
from counter import views
from django.http import JsonResponse

# Root uchun oddiy view
def home(request):
    return JsonResponse({
        'message': 'API ishlayapti',
        'endpoints': {
            'statistic_admin': '/statistic_admin/',
            'api_statistics': '/api/statistics/',
            'api_check_password': '/api/check-password/',
            'api_statistic_admin': '/api/statistic-admin/',
            'admin_panel': '/admin/'
        }
    })

urlpatterns = [
    path('', home, name='home'),  # <--- ROOT YO'NALISH
    path('admin/', admin.site.urls),
    path('api/statistics/', views.stats, name='stats'),
    path('api/check-password/', views.verify_statistic_password, name='check_password'),
    path('api/statistic-admin/', views.statistic_admin_session, name='statistic_admin_session'),
    path('api/statistic-logout/', views.statistic_logout, name='statistic_logout'),
    path('statistic_admin/', views.statistic_admin, name='statistic_admin'),
]
