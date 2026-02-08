from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # ==========================
    # 1. TRANG CHỦ & CƠ BẢN
    # ==========================
    path('', views.home, name='home'),
    path('map/', views.map_view, name='map'),

    # ==========================
    # 2. XE & CHI TIẾT THUÊ XE
    # ==========================
    path('thue-xe/', views.vehicle_list, name='vehicle_list'),
    path('thue-xe/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('thue-xe/<int:vehicle_id>/payment/', views.vehicle_payment, name='vehicle_payment'),
    
    # ==========================
    # 3. HỆ THỐNG XÁC THỰC (AUTH)
    # ==========================
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),

    # ==========================
    # 4. QUẢN LÝ ĐƠN HÀNG (USER)
    # ==========================
    path('my-orders/', views.order_list, name='order_list'),
    path('my-orders/<int:booking_id>/return/', views.booking_return, name='booking_return'),
    path('my-orders/<int:booking_id>/review/', views.review_form, name='review_form'),
    
    # ==========================================
    # 5. QUẢN TRỊ VIÊN (ADMIN DASHBOARD)
    # ==========================================
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Quản lý danh sách
    path('dashboard/vehicles/', views.admin_vehicle_list, name='admin_vehicles'),
    path('dashboard/bookings/', views.admin_booking_list, name='admin_bookings'),
    path('dashboard/stats/', views.admin_stats, name='admin_stats'),

    # CHỨC NĂNG QUẢN LÝ XE TÙY CHỈNH
    path('dashboard/vehicles/add/', views.admin_vehicle_create, name='admin_vehicle_add'),
    # Link sửa xe dùng để nạp dữ liệu vào form tùy chỉnh
    path('dashboard/vehicles/edit/<int:vehicle_id>/', views.admin_vehicle_edit, name='admin_vehicle_edit'),
    # Link xóa xe xử lý qua AJAX
    path('dashboard/vehicles/delete/<int:vehicle_id>/', views.admin_vehicle_delete, name='admin_vehicle_delete'),
    
    # TÁC VỤ QUẢN TRỊ NHANH
    path('dashboard/approve/<int:booking_id>/', views.approve_order, name='approve_order'),
    path('dashboard/vehicles/release/<int:vehicle_id>/', views.admin_release_vehicle, name='admin_release_vehicle'),
    path('dashboard/update-location/', views.update_vehicle_location, name='update_location'),
]