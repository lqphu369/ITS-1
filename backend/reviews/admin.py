from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # SỬA LẠI list_display CHO KHỚP MODEL MỚI:
    # - Dùng 'user' thay vì 'customer'
    # - Bỏ 'booking' (vì model mới đã bỏ trường này để giảm phụ thuộc)
    list_display = ('id', 'user', 'vehicle', 'rating', 'created_at')
    
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'vehicle__name')