from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

# Đã đổi từ GISDjango sang OSS
from OSS.controller import (
    suitability_controller,
    store_controller,
    cart_controller,
    auth_controller,
    order_controller, 
    views
)
from OSS import admin as custom_admin # Đổi từ GISDjango sang OSS

urlpatterns = [
    # --- 1. GIAO DIỆN KHÁCH HÀNG (STORE FRONT) ---
    path('', store_controller.home, name='home'),
    path('about-us/', views.aubout_us, name='about_us'),

    # [Auth] Xác thực - Các tên name='login', 'register' ở đây sẽ fix lỗi NoReverseMatch
    path('register/', auth_controller.register_view, name='register'),
    path('login/', auth_controller.login_view, name='login'),
    path('logout/', auth_controller.logout_view, name='logout'),
    path('profile/', auth_controller.profile_view, name='profile'),

    # [Products] Hiển thị sản phẩm
    path('products/', store_controller.product_list, name='product_list'),
    path('products/category/<slug:category_slug>/', store_controller.product_list, name='product_list_by_category'),
    path('products/<int:plant_id>/', store_controller.product_detail, name='product_detail'),

    # [GIS] Phân tích không gian
    path('check-suitability/', suitability_controller.suitability_page, name='check_suitability'),
    path('api/check/', suitability_controller.check_suitability_api, name='api_check_suitability'),
    path('store-map/', store_controller.store_locations_map, name='store_map'),

    # [Orders/Cart] Giỏ hàng & Đơn hàng của khách
    path('cart/', cart_controller.cart_detail, name='cart_detail'),
    path('cart/add/<int:plant_id>/', cart_controller.cart_add, name='cart_add'),
    path('cart/remove/<int:plant_id>/', cart_controller.cart_remove, name='cart_remove'),
    path('cart/checkout/', cart_controller.checkout, name='checkout'),
    path('order-success/', cart_controller.order_success_view, name='order_success'),
    path('my-orders/', cart_controller.user_order_list, name='user_order_list'),
    path('my-orders/<int:order_id>/', cart_controller.user_order_detail, name='order_detail'),
    path('my-orders/cancel/<int:order_id>/', order_controller.cancel_order, name='cancel_order'),

    # --- 2. HỆ THỐNG MẶC ĐỊNH (Django Admin) ---
    path('admin/', admin.site.urls),

    # --- 3. HỆ THỐNG QUẢN TRỊ RIÊNG (CUSTOM ADMIN TAILWIND) ---
    path('view/admin/dashboard/', custom_admin.dashboard, name='admin_dashboard'),

    # Quản lý Danh mục
    path('view/admin/categories/', custom_admin.category_management, name='admin_category_list'),
    path('view/admin/categories/add/', custom_admin.category_edit, name='category_add'),
    path('view/admin/categories/edit/<int:pk>/', custom_admin.category_edit, name='category_edit'),
    path('view/admin/categories/delete/<int:pk>/', custom_admin.category_delete, name='category_delete'),

    # Quản lý Cây cảnh
    path('view/admin/plants/', custom_admin.plant_management, name='admin_plant_list'),
    path('view/admin/plants/add/', custom_admin.plant_edit, name='plant_add'),
    path('view/admin/plants/edit/<int:pk>/', custom_admin.plant_edit, name='plant_edit'),
    path('view/admin/plants/delete/<int:pk>/', custom_admin.delete_plant, name='delete_plant'),

    # Quản lý Đơn hàng
    path('view/admin/orders/', custom_admin.order_management, name='admin_order_list'),
    path('view/admin/orders/<int:pk>/', custom_admin.order_detail, name='admin_order_detail'),

    # Quản lý Tồn kho
    path('view/admin/stocks/', custom_admin.stock_management, name='admin_stock_list'),
    path('view/admin/stocks/add/', custom_admin.stock_edit, name='stock_add'),
    path('view/admin/stocks/edit/<int:pk>/', custom_admin.stock_edit, name='stock_edit'),
    path('view/admin/stocks/delete/<int:pk>/', custom_admin.stock_delete, name='stock_delete'),

    # Quản lý Chi nhánh (GIS)
    path('view/admin/branches/', custom_admin.branch_management, name='admin_branch_list'),
    path('view/admin/branches/add/', custom_admin.branch_edit, name='branch_add'),
    path('view/admin/branches/edit/<int:pk>/', custom_admin.branch_edit, name='branch_edit'),
    path('view/admin/branches/delete/<int:pk>/', custom_admin.branch_delete, name='branch_delete'),

    # Quản lý tài khoản user
    path('view/admin/users/', custom_admin.user_management, name='admin_user_list'),
    path('view/admin/users/add/', custom_admin.user_edit, name='user_add'),
    path('view/admin/users/edit/<int:pk>/', custom_admin.user_edit, name='user_edit'),
    path('view/admin/users/delete/<int:pk>/', custom_admin.user_delete, name='user_delete'),
    path('view/admin/users/hard-delete/<int:pk>/', custom_admin.user_delete, name='user_hard_delete'),
    
    #path('contact-test/', mail_controller.contact_us, name='contact_us'),
]

# Cấu hình file Media và Static cho môi trường Development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)