# counter/views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from .models import Visitor, TotalRequest, AdminUser
from datetime import date, timedelta
import json
import requests

def login_page(request):
    return render(request, 'counter/login.html')

def get_country(ip):
    if ip.startswith(('192.168.', '10.', '172.')) or ip in ['0.0.0.0', '127.0.0.1']:
        return 'Tashkent'
    try:
        r = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        data = r.json()
        if data.get('status') == 'success':
            return data.get('country', 'Unknown')
    except:
        pass
    return 'Unknown'

@csrf_exempt
def track(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if not ip:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    if ',' in ip:
        ip = ip.split(',')[0].strip()
    
    total, _ = TotalRequest.objects.get_or_create(id=1)
    total.count += 1
    total.save()
    
    country = get_country(ip)
    Visitor.objects.get_or_create(ip=ip, defaults={'country': country})
    
    return JsonResponse({'status': 'ok'})

def statistics(request):
    total = TotalRequest.objects.first()
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    top5 = list(Visitor.objects.exclude(country__in=['Unknown', 'Local']).values('country').annotate(
        count=models.Count('id')).order_by('-count')[:5])
    
    return JsonResponse({
        'total_requests': total.count if total else 0,
        'total_visitors': Visitor.objects.count(),
        'today_visitors': Visitor.objects.filter(first_seen__date=today).count(),
        'week_visitors': Visitor.objects.filter(first_seen__date__gte=week_ago).count(),
        'top_countries': top5,
    })

@csrf_exempt
def admin_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        admin = AdminUser.objects.filter(username=username, password=password).first()
        
        if admin:
            request.session['admin_logged'] = True
            request.session['admin_username'] = admin.username
            return JsonResponse({'success': True, 'username': admin.username})
        else:
            return JsonResponse({'success': False, 'error': 'Wrong credentials'}, status=401)
    except:
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def admin_stats(request):
    if not request.session.get('admin_logged'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    total = TotalRequest.objects.first()
    today = date.today()
    
    all_countries = list(Visitor.objects.exclude(country__in=['Unknown', 'Local']).values('country').annotate(
        count=models.Count('id')).order_by('-count'))
    
    last_30_days = []
    for i in range(30):
        day = today - timedelta(days=i)
        last_30_days.append({
            'date': day.strftime('%Y-%m-%d'),
            'visitors': Visitor.objects.filter(first_seen__date=day).count()
        })
    
    return JsonResponse({
        'total_requests': total.count if total else 0,
        'total_visitors': Visitor.objects.count(),
        'today_visitors': Visitor.objects.filter(first_seen__date=today).count(),
        'all_countries': all_countries,
        'last_30_days': last_30_days,
    })

def admin_logout(request):
    request.session.flush()
    return JsonResponse({'success': True})