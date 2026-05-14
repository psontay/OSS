from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from OSS.controller import (
    suitability_controller,
    store_controller,
    cart_controller,
    auth_controller,
    order_controller,
    views,
    admin_branch_controller,
    admin_category_controller,
    admin_controller,
    admin_order_controller,
    admin_plant_controller,
    admin_stock_controller,
    admin_user_controller # Nhớ import thêm cái này
)

urlpatterns = [
    # --- 1. HỆ THỐNG MẶC ĐỊNH & LEGACY (Dành cho Web cũ hoặc Admin mặc định) ---
    path('admin/', admin.site.urls),
    path('', store_controller.home_api, name='home'),
    path('about-us/', views.about_us, name='about_us'),

    # --- 2. API V1 (Dành cho bạn làm Frontend Framework - React/Vue/Mobile) ---

    # [Auth API - JWT]
    path('api/v1/auth/register/', auth_controller.register_api, name='api_register'),
    path('api/v1/auth/login/', auth_controller.login_api, name='api_login'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('api/v1/auth/profile/', auth_controller.profile_api, name='api_profile'),
    # Nếu ông có làm các API verify OTP thì thêm ở đây:
    # path('api/v1/auth/verify-registration/', auth_controller.verify_registration_api, name='api_verify_reg'),

    # [Store & Products API]
    path('api/v1/home/', store_controller.home_api, name='api_home'),
    path('api/v1/products/', store_controller.product_list_api, name='api_products'),
    path('api/v1/products/<int:pk>/', store_controller.product_detail_api, name='api_product_detail'),
    path('api/v1/categories/', admin_category_controller.category_list_api, name='api_public_categories'),

    # [GIS API]
    path('api/v1/gis/check-suitability/', suitability_controller.check_suitability_api, name='api_check_env'),
    path('api/v1/gis/store-locations/', store_controller.store_locations_api, name='api_store_locations'),

    # [Customer Orders API]
    path('api/v1/orders/checkout/', order_controller.api_checkout, name='api_checkout'), # Thống nhất dùng cái này
    path('api/v1/orders/history/', order_controller.api_order_list, name='api_order_list'),
    path('api/v1/orders/<int:pk>/', order_controller.api_order_detail, name='api_order_detail'),
    path('api/v1/orders/<int:pk>/cancel/', order_controller.api_cancel_order, name='api_cancel_order'),

    # --- 3. ADMIN API (Dành cho giao diện quản trị mới) ---

    path('api/v1/admin/dashboard/', admin_controller.dashboard_api, name='api_admin_dashboard'),

    # Admin - Quản lý Danh mục
    path('api/v1/admin/categories/', admin_category_controller.category_list_api, name='api_admin_category_list'),
    path('api/v1/admin/categories/create/', admin_category_controller.category_create_api, name='api_admin_category_create'),
    path('api/v1/admin/categories/<int:pk>/', admin_category_controller.category_detail_api, name='api_admin_category_detail'),
    path('api/v1/admin/categories/<int:pk>/delete/', admin_category_controller.category_delete_api, name='api_admin_category_delete'),

    # Admin - Quản lý Cây cảnh
    path('api/v1/admin/plants/', admin_plant_controller.plant_list_api, name='api_admin_plant_list'),
    path('api/v1/admin/plants/create/', admin_plant_controller.plant_create_api, name='api_admin_plant_create'),
    path('api/v1/admin/plants/<int:pk>/', admin_plant_controller.plant_detail_api, name='api_admin_plant_detail'),
    path('api/v1/admin/plants/<int:pk>/delete/', admin_plant_controller.plant_delete_api, name='api_admin_plant_delete'),

    # Admin - Quản lý Đơn hàng
    path('api/v1/admin/orders/', admin_order_controller.order_list_api, name='api_admin_order_list'),
    path('api/v1/admin/orders/<int:pk>/', admin_order_controller.order_detail_api, name='api_admin_order_detail'),
    path('api/v1/admin/orders/<int:pk>/update-status/', admin_order_controller.order_update_status_api, name='api_admin_order_update'),

    # Admin - Quản lý Tồn kho
    path('api/v1/admin/stocks/', admin_stock_controller.stock_list_api, name='api_admin_stock_list'),
    path('api/v1/admin/stocks/create/', admin_stock_controller.stock_create_api, name='api_admin_stock_create'),
    path('api/v1/admin/stocks/<int:pk>/', admin_stock_controller.stock_detail_api, name='api_admin_stock_detail'),
    path('api/v1/admin/stocks/<int:pk>/delete/', admin_stock_controller.stock_delete_api, name='api_admin_stock_delete'),

    # Admin - Quản lý Chi nhánh
    path('api/v1/admin/branches/', admin_branch_controller.branch_list_api, name='api_admin_branch_list'),
    path('api/v1/admin/branches/create/', admin_branch_controller.branch_create_api, name='api_admin_branch_create'),
    path('api/v1/admin/branches/<int:pk>/', admin_branch_controller.branch_detail_api, name='api_admin_branch_detail'),
    path('api/v1/admin/branches/<int:pk>/delete/', admin_branch_controller.branch_delete_api, name='api_admin_branch_delete'),

    # Admin - Quản lý User (Đã chuyển sang API)
    path('api/v1/admin/users/', admin_user_controller.user_list_api, name='api_admin_user_list'),
    path('api/v1/admin/users/<int:pk>/delete/', admin_user_controller.user_delete_api, name='api_admin_user_delete'),
]

# Cấu hình file Media và Static
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)