from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def test_api_view(request):
    try:
        data = json.loads(request.body)
        date = data.get('date')
        return JsonResponse({'result': f'received: {date}'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 