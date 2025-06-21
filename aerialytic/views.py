from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .pv_modeling.optimal_orientation import get_optimal_orientation

@csrf_exempt
@require_POST
def test_api_view(request):
    try:
        data = json.loads(request.body)
        date = data.get('date')
        return JsonResponse({'result': f'received: {date}'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def solar_geometry_api_view(request):
    try:
        data = json.loads(request.body)
        
        # Validate and normalize latitude (-90 to 90)
        latitude_raw = float(data.get('latitude'))
        if latitude_raw < -360 or latitude_raw > 360:
            raise ValueError("Latitude must be between -360 and 360")
        latitude = ((latitude_raw + 90) % 180) - 90  # Normalize to -90 to 90
        
        # Validate and normalize longitude (-180 to 180)
        longitude_raw = float(data.get('longitude'))
        if longitude_raw < -360 or longitude_raw > 360:
            raise ValueError("Longitude must be between -360 and 360")
        longitude = ((longitude_raw + 180) % 360) - 180  # Normalize to -180 to 180
        
        offset = 0.0 if data.get('offset') is None else float(data.get('offset'))
        
        # Validate offset (ground slope angle should be reasonable)
        if offset < -90 or offset > 90:
            raise ValueError("Offset (ground slope) must be between -90 and 90 degrees")
        
        result = get_optimal_orientation(latitude, longitude, offset)
        
        return JsonResponse({
            'latitude': latitude,
            'longitude': longitude,
            'offset': offset,
            'optimal_tilt': result['optimal_tilt'],
            'optimal_azimuth': result['optimal_azimuth'],
            'effective_tilt': result['effective_tilt'],
            'annual_irradiance_kwh_m2': round(result['annual_irradiance_kwh_m2'], 2)
        })
    except ValueError as e:
        return JsonResponse({'error': f'Invalid input values: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 