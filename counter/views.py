# ... boshqa importlar
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

STATISTIC_PASSWORD = "stat123"

@csrf_exempt
@require_http_methods(["POST"])
def verify_statistic_password(request):
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
        
        if password == STATISTIC_PASSWORD:
            request.session['statistic_auth'] = True
            request.session.set_expiry(300)  # 5 daqiqa
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False}, status=401)
    except:
        return JsonResponse({'success': False}, status=400)


def statistic_admin_secure(request):
    if not request.session.get('statistic_auth'):
        return JsonResponse({'error': 'Unauthorized', 'need_auth': True}, status=401)
    
    # ... statistikani qaytarish
