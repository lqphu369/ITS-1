from django.contrib import admin
from .models import Vehicle, VehicleImage 

# 1. Phần Upload ảnh
class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 4

# 2. Phần Quản lý Xe
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # Danh sách hiển thị phục vụ Map
    list_display = (
        'id',
        'name',
        'license_plate',
        'vehicle_type',
        'status',          # Quan trọng cho Map đổi màu
        'price_per_day',
        'latitude',        # Quan trọng cho Map
        'longitude',       # Quan trọng cho Map
        'created_at',
    )

    list_filter = ('status', 'vehicle_type')
    search_fields = ('name', 'license_plate')
    
    # Tích hợp upload ảnh
    inlines = [VehicleImageInline]