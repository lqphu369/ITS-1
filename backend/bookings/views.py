import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404

from .models import Booking
from vehicles.models import Vehicle
from .utils import is_overlapping, calc_total_price


def is_admin(user):
    return user.is_authenticated and user.is_staff


def _vehicle_booked_code():
    return "rented"


@csrf_exempt
@login_required
def create_booking(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        vehicle_id = int(payload["vehicle_id"])
        start_date = payload["start_date"]
        end_date = payload["end_date"]
    except Exception:
        return JsonResponse({"detail": "Invalid JSON/body"}, status=400)

    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    from datetime import date
    try:
        s = date.fromisoformat(start_date)
        e = date.fromisoformat(end_date)
    except Exception:
        return JsonResponse({"detail": "start_date/end_date phải dạng YYYY-MM-DD"}, status=400)

    if e < s:
        return JsonResponse({"detail": "end_date phải >= start_date"}, status=400)

    # SỬA: Cho phép đặt xe nếu trạng thái là 'available' HOẶC nếu đặt cho tương lai (status khác nhưng không trùng lịch)
    # Chúng ta bỏ qua check status cứng nhắc này, vì hàm is_overlapping bên dưới sẽ lo việc kiểm tra trùng lịch.
    
    # if getattr(vehicle, "status", "") != "available":
    #    return JsonResponse({"detail": "Xe không sẵn sàng"}, status=400)
    
    # Thay vào đó, chỉ chặn nếu xe đang 'maintenance' (Bảo trì) vì bảo trì thường không biết ngày xong
    if str(getattr(vehicle, "status", "")).lower() in ["maintenance", "bao tri"]:
         return JsonResponse({"detail": "Xe đang bảo trì, không thể đặt lúc này"}, status=400)

    if is_overlapping(vehicle, s, e):
        return JsonResponse({"detail": "Xe bị trùng lịch"}, status=400)

    total = calc_total_price(vehicle, s, e)

    booking = Booking.objects.create(
        user=request.user,
        vehicle=vehicle,
        start_date=s,
        end_date=e,
        total_price=total,
        status="pending",
    )

    return JsonResponse({
        "id": booking.id,
        "status": booking.status,
        "total_price": str(booking.total_price),
        "vehicle_id": booking.vehicle_id,
        "start_date": str(booking.start_date),
        "end_date": str(booking.end_date),
    }, status=201)


@login_required
def my_bookings(request):
    qs = Booking.objects.filter(user=request.user).select_related("vehicle").order_by("-id")
    data = []
    for b in qs:
        data.append({
            "id": b.id,
            "status": b.status,
            "total_price": str(b.total_price),
            "vehicle": {
                "id": b.vehicle_id,
                "license_plate": getattr(b.vehicle, "license_plate", ""),
                "name": getattr(b.vehicle, "name", ""),
            },
            "start_date": str(b.start_date),
            "end_date": str(b.end_date),
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
@login_required
def cancel_booking(request, booking_id: int):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    b = get_object_or_404(Booking, id=booking_id)

    if (not request.user.is_staff) and b.user_id != request.user.id:
        return JsonResponse({"detail": "Không có quyền huỷ booking này"}, status=403)

    if b.status not in ("pending", "approved"):
        return JsonResponse({"detail": "Không thể huỷ ở trạng thái này"}, status=400)

    b.status = "cancelled"
    b.save(update_fields=["status"])

    v = b.vehicle
    v.status = "available"
    v.save(update_fields=["status"])

    return JsonResponse({"id": b.id, "status": b.status})


@csrf_exempt
@user_passes_test(is_admin)
def approve_booking(request, booking_id: int):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    b = get_object_or_404(Booking, id=booking_id)

    if b.status != "pending":
        return JsonResponse({"detail": "Chỉ duyệt booking pending"}, status=400)

    b.status = "approved"
    b.save(update_fields=["status"])

    v = b.vehicle
    v.status = _vehicle_booked_code()
    v.save(update_fields=["status"])

    return JsonResponse({"id": b.id, "status": b.status})


@csrf_exempt
@user_passes_test(is_admin)
def complete_booking(request, booking_id: int):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    b = get_object_or_404(Booking, id=booking_id)

    if b.status != "approved":
        return JsonResponse({"detail": "Chỉ complete booking approved"}, status=400)

    b.status = "completed"
    b.save(update_fields=["status"])

    v = b.vehicle
    v.status = "available"
    v.save(update_fields=["status"])

    return JsonResponse({"id": b.id, "status": b.status})
