from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Q

ACTIVE_STATUSES = ("pending", "approved")


def dates_in_range(start: date, end: date):
    """Yield từng ngày từ start -> end (inclusive)."""
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def is_weekend(d: date) -> bool:
    """T7/CN."""
    return d.weekday() >= 5  # 5=Sat, 6=Sun


def get_unit_price_per_day(vehicle) -> Decimal:
    """
    Lấy giá theo ngày từ vehicle.
    Ưu tiên price_per_day, fallback price_per_hour*24 
    """
    if hasattr(vehicle, "price_per_day") and vehicle.price_per_day is not None:
        return Decimal(str(vehicle.price_per_day))
    if hasattr(vehicle, "price_per_hour") and vehicle.price_per_hour is not None:
        return (Decimal(str(vehicle.price_per_hour)) * Decimal("24")).quantize(Decimal("0.01"))
    return Decimal("0.00")


def calc_total_price(vehicle, start_date: date, end_date: date) -> Decimal:
    """
    Dynamic Pricing: cuối tuần +20% (T7, CN).
    Tính theo từng ngày để đúng logic 
    """
    base = get_unit_price_per_day(vehicle)
    if end_date < start_date:
        return Decimal("0.00")

    total = Decimal("0.00")
    for d in dates_in_range(start_date, end_date):
        multiplier = Decimal("1.20") if is_weekend(d) else Decimal("1.00")
        total += (base * multiplier)

    return total.quantize(Decimal("0.01"))


def is_overlapping(vehicle, start_date: date, end_date: date) -> bool:
    """
    Check trùng lịch: existing.start <= new.end AND existing.end >= new.start
    Chỉ xét booking còn active (pending/approved).
    """
    return vehicle.bookings.filter(status__in=ACTIVE_STATUSES).filter(
        Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
    ).exists()
