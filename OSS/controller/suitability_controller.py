import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models.plant import Plant

@api_view(['GET'])
def check_suitability_api(request):
    """
    API Phân tích GIS: Kết hợp thời tiết (Open-Meteo) và Dữ liệu đất (ISRIC)
    """
    plant_id = request.query_params.get('plant_id')
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lng')

    if not all([plant_id, lat, lon]):
        return Response({
            "status": "error",
            "message": "Thiếu thông tin tọa độ hoặc ID cây trồng."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        plant = get_object_or_404(Plant, id=plant_id)

        # --- 1. GỌI API THỜI TIẾT (OPEN-METEO) ---
        current_temp = 25.0
        current_humidity = 50.0
        elevation = 0

        try:
            weather_url = "https://api.open-meteo.com/v1/forecast"
            w_params = {
                'latitude': lat, 'longitude': lon,
                'current_weather': 'true', 'hourly': 'relativehumidity_2m'
            }
            resp_w = requests.get(weather_url, params=w_params, timeout=5)
            if resp_w.status_code == 200:
                w_data = resp_w.json()
                current_temp = w_data.get('current_weather', {}).get('temperature', 25.0)
                current_humidity = w_data.get('hourly', {}).get('relativehumidity_2m', [50])[0]
                elevation = w_data.get('elevation', 0)
        except Exception:
            pass # Giữ mặc định nếu API thời tiết sập

        # --- 2. GỌI API DỮ LIỆU ĐẤT (ISRIC SOILGRIDS) ---
        actual_ph = 6.0
        actual_clay = 15.0

        try:
            soil_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
            # Lưu ý: requests xử lý params trùng tên bằng list tuple
            soil_params = [
                ('lon', lon), ('lat', lat),
                ('property', 'phh2o'), ('property', 'clay'),
                ('depth', '0-5cm'), ('value', 'mean')
            ]
            resp_s = requests.get(soil_url, params=soil_params, timeout=10)
            if resp_s.status_code == 200:
                s_data = resp_s.json()
                layers = s_data.get('properties', {}).get('layers', [])
                for layer in layers:
                    val = layer['depths'][0]['values']['mean']
                    if val is not None:
                        if layer['name'] == 'phh2o':
                            actual_ph = val / 10.0
                        elif layer['name'] == 'clay':
                            actual_clay = val / 10.0
        except Exception:
            pass # Giữ mặc định nếu API đất sập

        # --- 3. ĐÁNH GIÁ (Logic Model của ông) ---
        is_suitable, reasons = plant.check_environment_advanced(
            current_temp, actual_ph, current_humidity, actual_clay
        )

        message = "✅ Rất phù hợp để trồng!" if is_suitable else f"⚠️ {', '.join(reasons)}"

        return Response({
            "status": "success",
            "data": {
                "plant_name": plant.name,
                "suitable": is_suitable,
                "message": message,
                "details": {
                    "temp": f"{current_temp}°C",
                    "ph": f"{actual_ph}",
                    "humidity": f"{current_humidity}%",
                    "soil_type": f"Sét {actual_clay}%",
                    "elevation": f"{elevation}m"
                }
            }
        })

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Lỗi hệ thống GIS: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)