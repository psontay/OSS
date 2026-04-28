from django.shortcuts import render
from django.http import JsonResponse
from ..model.plant import Plant
import requests

def suitability_page(request):
    plants = Plant.objects.all()
    return render(request, 'gis/check_suitability.html', {'plants': plants})


def check_suitability_api(request):
    plant_id = request.GET.get('plant_id')
    lat = request.GET.get('lat')
    lon = request.GET.get('lng')

    if not all([plant_id, lat, lon]):
        return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin (ID, Lat, Lng)'})

    try:
        plant = Plant.objects.get(id=plant_id)
        # --- 1. OPEN-METEO (Thời tiết) ---
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': 'true',
            'hourly': 'relativehumidity_2m'
        }

        # Thiết lập giá trị mặc định phòng khi API lỗi
        current_temp = 25.0
        current_humidity = 50.0
        elevation = 0

        try:
            resp_w = requests.get(weather_url, params=weather_params, timeout=5)
            if resp_w.status_code == 200:
                w_data = resp_w.json()
                current_temp = w_data.get('current_weather', {}).get('temperature', 25.0)
                current_humidity = w_data.get('hourly', {}).get('relativehumidity_2m', [50])[0]
                elevation = w_data.get('elevation', 0)
        except:
            pass # Giữ giá trị mặc định nếu API thời tiết lỗi

        # --- 2. ISRIC (Đất & pH) ---
        soil_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        # ISRIC yêu cầu gửi nhiều params cùng tên 'property'
        soil_params = [
            ('lon', lon), ('lat', lat),
            ('property', 'phh2o'), ('property', 'clay'),
            ('depth', '0-5cm'), ('value', 'mean')
        ]

        actual_ph = 6.0 # Mặc định
        actual_clay = 15.0 # Mặc định

        try:
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
        except:
            pass # Giữ giá trị mặc định nếu API đất lỗi

        # --- 3. ĐÁNH GIÁ (Dùng hàm mới check_environment_advanced) ---
        # Giữ nguyên thứ tự tham số: temp, ph, humidity, clay_percent
        is_suitable, reasons = plant.check_environment_advanced(
            current_temp, actual_ph, current_humidity, actual_clay
        )

        # Giữ nguyên cấu trúc trả về như bạn ông viết
        message = "✅ Rất phù hợp để trồng!" if is_suitable else f"⚠️ {', '.join(reasons)}"

        return JsonResponse({
            'status': 'success',
            'suitable': is_suitable, # Tên biến cũ
            'message': message,
            'data': { # Giữ nguyên object data
                'temp': f"{current_temp}°C",
                'ph': f"{actual_ph}",
                'humidity': f"{current_humidity}%",
                'soil_type': f"Sét {actual_clay}%",
                'elevation': f"{elevation}m"
            }
        })

    except Plant.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy cây trồng'})
    except Exception as e:
        # Bắt lỗi hệ thống để không văng lỗi 500 HTML làm JS bị lỗi 'char 0'
        return JsonResponse({'status': 'error', 'message': f'Lỗi GIS: {str(e)}'})