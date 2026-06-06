import requests
from ipware import get_client_ip

def get_location_from_ip(request):
    client_ip, is_routable = get_client_ip(request)
    
    if not client_ip or client_ip == '127.0.0.1' or client_ip.startswith('192.168.'):
        return "Uzbekistan", "Tashkent"
    
    try:
        response = requests.get(f'http://ip-api.com/json/{client_ip}', timeout=3)
        data = response.json()
        
        if data.get('status') == 'success':
            country = data.get('country', 'Uzbekistan')
            city = data.get('city', 'Tashkent')
            
            if country == 'Uzbekistan' and city not in ['Tashkent', 'Andijan', 'Samarkand']:
                city = 'Tashkent'
            
            if country == 'Russia' and city not in ['Moscow', 'Saint Petersburg']:
                city = 'Moscow'
            
            return country, city
        else:
            return "Uzbekistan", "Tashkent"
            
    except Exception as e:
        print(f"GeoIP error: {e}")
        return "Uzbekistan", "Tashkent"

