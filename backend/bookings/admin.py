from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'vehicle',
        'start_date',
        'end_date',
        'total_price',
        'status',
        'created_at',
    )

    list_filter = ('status', 'start_date')
    search_fields = ('customer__username', 'vehicle__license_plate')
