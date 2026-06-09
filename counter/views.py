# counter/views.py
from django.http import JsonResponse
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Visitor, TotalRequest
from datetime import date, datetime, timedelta
import json
import base64
import requests

STATISTIC_PASSWORD = "stat123"
STATISTIC_USERNAME = "stat_admin"

def get_country(ip):
    if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
        return 'Tashkent'
    if ip in ['0.0.0.0', '127.0.0.1', 'localhost']:
        return 'Tashkent'
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        data = response.json()
        if data.get('status') == 'success':
            return data.get('country', 'Unknown')
    except:
        pass
    return 'Unknown'

@csrf_exempt
@require_http_methods(["POST"])
def track_visit(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if not ip:
        ip = request.META.get('REMOTE_ADDR')
    if not ip:
        ip = '0.0.0.0'
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    
    total, _ = TotalRequest.objects.get_or_create(id=1)
    total.count += 1
    total.save()
    
    country = get_country(ip)
    visitor, created = Visitor.objects.get_or_create(ip=ip, defaults={'country': country})
    if not created and visitor.country == 'Unknown':
        visitor.country = country
        visitor.save()
    
    return JsonResponse({'status': 'ok'})

def stats(request):
    today = date.today()
    period = request.GET.get('period', 'all')
    
    total_requests_obj = TotalRequest.objects.first()
    total_requests_count = total_requests_obj.count if total_requests_obj else 0
    total_visitors = Visitor.objects.count()
    
    top_5_countries = list(Visitor.objects.exclude(country__in=['Unknown', 'Local']).values('country').annotate(
        count=models.Count('id')).order_by('-count')[:5])
    
    today_start = datetime.combine(today, datetime.min.time())
    today_visitors = Visitor.objects.filter(first_seen__gte=today_start).count()
    
    daily_stats = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_visitors = Visitor.objects.filter(first_seen__date=day).count()
        daily_stats.append({'date': day.strftime('%Y-%m-%d'), 'visitors': day_visitors})
    
    monthly_stats = []
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=30*i)
        month_start = date(month_date.year, month_date.month, 1)
        month_visitors = Visitor.objects.filter(
            first_seen__date__year=month_start.year,
            first_seen__date__month=month_start.month
        ).count()
        monthly_stats.append({'month': month_start.strftime('%Y-%m'), 'visitors': month_visitors})
    
    response_data = {
        'total_visitors': total_visitors,
        'total_requests': total_requests_count,
        'today_visitors': today_visitors,
        'top_5_countries': top_5_countries,
    }
    
    if period == 'day':
        response_data['data'] = daily_stats
    elif period == 'month':
        response_data['data'] = monthly_stats
    else:
        response_data['daily'] = daily_stats
        response_data['monthly'] = monthly_stats
    
    return JsonResponse(response_data)

def basic_auth_required(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Basic '):
            response = JsonResponse({'error': 'Unauthorized'}, status=401)
            response['WWW-Authenticate'] = 'Basic realm="Statistics Admin"'
            return response
        try:
            auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = auth_decoded.split(':', 1)
            if username == STATISTIC_USERNAME and password == STATISTIC_PASSWORD:
                return view_func(request, *args, **kwargs)
        except:
            pass
        response = JsonResponse({'error': 'Invalid credentials'}, status=401)
        response['WWW-Authenticate'] = 'Basic realm="Statistics Admin"'
        return response
    return wrapper

@basic_auth_required
def statistic_admin(request):
    total_requests_obj = TotalRequest.objects.first()
    total_requests = total_requests_obj.count if total_requests_obj else 0
    total_visitors = Visitor.objects.count()
    
    yearly = []
    for year_date in Visitor.objects.dates('first_seen', 'year').distinct():
        yearly.append({'year': year_date.year, 'visitors': Visitor.objects.filter(first_seen__date__year=year_date.year).count()})
    
    monthly = []
    for month_date in Visitor.objects.dates('first_seen', 'month').distinct():
        monthly.append({'month': month_date.strftime('%Y-%m'), 'visitors': Visitor.objects.filter(
            first_seen__date__year=month_date.year, first_seen__date__month=month_date.month).count()})
    
    daily = []
    for day_date in Visitor.objects.dates('first_seen', 'day').distinct():
        daily.append({'date': day_date.strftime('%Y-%m-%d'), 'visitors': Visitor.objects.filter(first_seen__date=day_date).count()})
    
    top_5_countries = list(Visitor.objects.exclude(country__in=['Unknown', 'Local']).values('country').annotate(
        count=models.Count('id')).order_by('-count')[:5])
    
    return JsonResponse({
        'total_visitors': total_visitors,
        'total_requests': total_requests,
        'yearly': yearly,
        'monthly': monthly,
        'daily': daily,
        'top_5_countries': top_5_countries,
    })

@csrf_exempt
@require_http_methods(["POST"])
def verify_statistic_password(request):
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
        if password == STATISTIC_PASSWORD:
            request.session['statistic_auth'] = True
            request.session.set_expiry(3600)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False}, status=401)
    except:
        return JsonResponse({'success': False}, status=400)

@csrf_exempt
def statistic_admin_session(request):
    if not request.session.get('statistic_auth'):
        return JsonResponse({'error': 'Unauthorized', 'need_auth': True}, status=401)
    
    total_requests_obj = TotalRequest.objects.first()
    total_requests = total_requests_obj.count if total_requests_obj else 0
    total_visitors = Visitor.objects.count()
    
    yearly = []
    for year_date in Visitor.objects.dates('first_seen', 'year').distinct():
        yearly.append({'year': year_date.year, 'visitors': Visitor.objects.filter(first_seen__date__year=year_date.year).count()})
    
    monthly = []
    for month_date in Visitor.objects.dates('first_seen', 'month').distinct():
        monthly.append({'month': month_date.strftime('%Y-%m'), 'visitors': Visitor.objects.filter(
            first_seen__date__year=month_date.year, first_seen__date__month=month_date.month).count()})
    
    daily = []
    for day_date in Visitor.objects.dates('first_seen', 'day').distinct():
        daily.append({'date': day_date.strftime('%Y-%m-%d'), 'visitors': Visitor.objects.filter(first_seen__date=day_date).count()})
    
    top_5_countries = list(Visitor.objects.exclude(country__in=['Unknown', 'Local']).values('country').annotate(
        count=models.Count('id')).order_by('-count')[:5])
    
    return JsonResponse({
        'total_visitors': total_visitors,
        'total_requests': total_requests,
        'yearly': yearly,
        'monthly': monthly,
        'daily': daily,
        'top_5_countries': top_5_countries,
    })

def statistic_logout(request):
    request.session.flush()
    return JsonResponse({'success': True})