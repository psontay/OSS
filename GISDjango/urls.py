from django.contrib import admin
from django.urls import path
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    # Đã đổi sang /products/ cho ngắn gọn
    path('products/', views.product_list, name='product_list'), 
    # Trang giao diện bản đồ
    path('check-suitability/', views.suitability_page, name='check_suitability'), 
    # API xử lý dữ liệu PostGIS (gọi bằng fetch trong JS)
    path('api/check/', views.check_suitability, name='api_check_suitability'), 
]