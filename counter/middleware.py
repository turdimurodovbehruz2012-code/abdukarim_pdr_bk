# counter/middleware.py
from .models import Visitor, TotalRequest
import requests

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

class CounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path == '/':
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
        
        response = self.get_response(request)
        return response