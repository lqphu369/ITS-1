from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q, Sum
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from datetime import datetime, timedelta

# Import Forms
from .forms import (
    RegistrationForm, UserLoginForm, 
    ReviewForm, VehicleForm
)

# --- IMPORT MODELS ---
try:
    from vehicles.models import Vehicle
    from bookings.models import Booking
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    Vehicle = None
    Booking = None
    User = None

# Hàm kiểm tra quyền Admin chuyên sâu
def is_admin(user):
    return user.is_authenticated and user.is_staff

# ==========================================
# 1. PUBLIC VIEWS (DÀNH CHO MỌI NGƯỜI)
# ==========================================

def home(request):
    if Vehicle:
        vehicles = Vehicle.objects.all().order_by('-id')[:8]
    else:
        vehicles = []

    vehicle_name = request.GET.get('q')
    vehicle_type = request.GET.get('type')

    if vehicle_name and vehicles:
        vehicles = vehicles.filter(name__icontains=vehicle_name)
    if vehicle_type and vehicles: 
        vehicles = vehicles.filter(vehicle_type=vehicle_type) 

    return render(request, 'pages/home.html', {'featured_vehicles': vehicles})

def map_view(request):
    if not Vehicle:
        return render(request, 'pages/map.html', {'vehicles': [], 'vehicles_json': []})

    vehicles = Vehicle.objects.exclude(Q(latitude__isnull=True) | Q(longitude__isnull=True))
    vehicles_json = []
    
    for v in vehicles:
        lat = getattr(v, 'latitude', 0) or getattr(v, 'lat', 0)
        lng = getattr(v, 'longitude', 0) or getattr(v, 'lng', 0)
        
        vehicles_json.append({
            'id': v.id,
            'name': getattr(v, 'name', 'Xe'),
            'lat': float(lat),
            'lng': float(lng),
            'status': getattr(v, 'status', 'Available'),
            'status_display': v.get_status_display() if hasattr(v, 'get_status_display') else str(v.status),
            'image_url': v.image.url if v.image else '/static/img/placeholder.jpg',
            'detail_url': reverse('frontend:vehicle_detail', args=[v.id]),
            'price': float(getattr(v, 'price_per_day', 0) or getattr(v, 'daily_rate', 0)),
            'rating': 4.8, 
            'trips': 12 
        })

    return render(request, 'pages/map.html', {
        'vehicles': vehicles, 
        'vehicles_json': vehicles_json
    })

def vehicle_list(request):
    vehicles = Vehicle.objects.all()

    # ===== LỌC THEO LOẠI XE =====
    vehicle_type = request.GET.get('vehicle_type')
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)

    # ===== SẮP XẾP =====
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        vehicles = vehicles.order_by('price_per_day')
    elif sort_by == 'price_desc':
        vehicles = vehicles.order_by('-price_per_day')
    else:
        vehicles = vehicles.order_by('-id')

    context = {
        'vehicles': vehicles
    }
    return render(request, 'vehicles/list.html', context)


def vehicle_detail(request, vehicle_id):
    from reviews.models import Review
    from django.db.models import Avg
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    reviews = Review.objects.filter(vehicle=vehicle).order_by('-created_at')
    
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    
    review_count = reviews.count()
    
    return render(request, 'vehicles/detail.html', {
        'vehicle': vehicle,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
    })

# ==========================================
# 2. USER OPERATIONS (DÀNH CHO NGƯỜI THUÊ)
# ==========================================

@login_required(login_url='frontend:login')
def vehicle_payment(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    
    # Lấy thông tin ngày từ POST hoặc GET (hỗ trợ chuyển hướng từ Map)
    pickup_str = request.POST.get('pickup_date') or request.GET.get('pickup_date', '')
    return_str = request.POST.get('return_date') or request.GET.get('return_date', '')
    
    try:
        p_date = datetime.strptime(pickup_str.split(',')[0].strip(), "%Y-%m-%d").date()
        r_date = datetime.strptime(return_str.split(',')[0].strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError, IndexError, TypeError):
        p_date = datetime.now().date()
        r_date = p_date + timedelta(days=1) 

    # --- LOGIC TÍNH TOÁN ĐỒNG BỘ VỚI UI (SURGE PRICING 20%) ---
    weekday_count = 0
    weekend_count = 0
    daily_rate = float(vehicle.price_per_day)
    
    current_date = p_date
    while current_date < r_date:
        if current_date.weekday() >= 5: # 5 là Thứ 7, 6 là Chủ nhật
            weekend_count += 1
        else:
            weekday_count += 1
        current_date += timedelta(days=1)

    weekday_total = weekday_count * daily_rate
    weekend_rate = daily_rate * 1.2
    weekend_total = weekend_count * weekend_rate
    base_total = weekday_total + weekend_total
    tax_fee = base_total * 0.1
    final_total = base_total + tax_fee

    # Xử lý xác nhận thanh toán
    if request.method == 'POST' and 'payment_method' in request.POST:
        try:
            Booking.objects.create(
                customer=request.user,
                vehicle=vehicle,
                start_date=p_date,
                end_date=r_date,
                total_price=final_total,
                status='pending'
            )
            vehicle.status = 'Booked'
            vehicle.save()
            messages.success(request, "Thanh toán thành công! Đơn hàng đang chờ xác nhận.")
            return redirect('/my-orders/') 
        except Exception as e:
            messages.error(request, f"Lỗi hệ thống: {str(e)}")
            return redirect(f'/thue-xe/{vehicle_id}/')

    return render(request, 'bookings/payment.html', {
        'vehicle': vehicle,
        'pickup_date': p_date,
        'return_date': r_date,
        'days': weekday_count + weekend_count,
        'weekday_count': weekday_count,
        'weekend_count': weekend_count, # Đảm bảo biến này được truyền để UI hiển thị số ngày cuối tuần
        'weekday_total': weekday_total,
        'weekend_total': weekend_total,
        'weekend_rate': weekend_rate,
        'tax_fee': tax_fee,
        'final_total': final_total
    })

@login_required(login_url='frontend:login')
def order_list(request):
    from reviews.models import Review
    if not Booking:
        return render(request, 'bookings/my_list.html', {'bookings': []})
    try:
        bookings_qs = Booking.objects.filter(customer=request.user).order_by('-id')
        status_filter = request.GET.get('status')
        search_query = request.GET.get('q')

        if status_filter and status_filter != 'all':
            bookings_qs = bookings_qs.filter(status=status_filter)
        if search_query:
            bookings_qs = bookings_qs.filter(Q(vehicle__name__icontains=search_query) | Q(vehicle__license_plate__icontains=search_query))

        reviewed_vehicle_ids = list(Review.objects.filter(user=request.user).values_list('vehicle_id', flat=True))

        all_user_bookings = Booking.objects.filter(customer=request.user)
        context = {
            'bookings': bookings_qs,
            'reviewed_vehicle_ids': reviewed_vehicle_ids,
            'active_count': all_user_bookings.filter(status='approved').count(),
            'completed_count': all_user_bookings.filter(status='completed').count(),
            'pending_count': all_user_bookings.filter(status='pending').count(),
        }
    except Exception as e:
        messages.error(request, f"Lỗi hiển thị danh sách: {str(e)}")
        context = {'bookings': [], 'reviewed_vehicle_ids': [], 'active_count': 0, 'completed_count': 0, 'pending_count': 0}
    return render(request, 'bookings/my_list.html', context)

@login_required(login_url='frontend:login')
def booking_return(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)
    if request.method == 'POST':
        booking.status = 'completed'
        booking.vehicle.status = 'Available' 
        booking.vehicle.save()
        booking.save()
        messages.success(request, "Trả xe thành công!")
        return redirect('/my-orders/')
    return render(request, 'bookings/return.html', {'booking': booking})

@login_required(login_url='frontend:login')
def review_form(request, booking_id):
    from reviews.models import Review
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)
    existing_review = Review.objects.filter(user=request.user, vehicle=booking.vehicle).first()
    if existing_review:
        messages.info(request, "Bạn đã đánh giá xe này rồi!")
        return redirect('/my-orders/')
    
    if booking.status != 'completed':
        messages.error(request, "Chỉ có thể đánh giá sau khi hoàn thành chuyến đi!")
        return redirect('/my-orders/')
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.vehicle = booking.vehicle
            review.save()
            messages.success(request, "Cảm ơn bạn đã gửi đánh giá!")
            return redirect('/my-orders/')
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin đánh giá.")
    else:
        form = ReviewForm()
    return render(request, 'reviews/form.html', {'booking': booking, 'form': form})

# ==========================================
# 3. ADMIN OPERATIONS (DÀNH CHO QUẢN TRỊ)
# ==========================================

@user_passes_test(is_admin, login_url='frontend:login')
def admin_dashboard(request):
    total_rev = Booking.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    new_bookings = Booking.objects.filter(status='pending').count()
    active_rentals = Booking.objects.filter(status='approved').count()
    recent_activities = Booking.objects.all().order_by('-created_at')[:10]
    vehicles = Vehicle.objects.all()

    context = {
        'total_revenue': total_rev,
        'new_bookings_count': new_bookings,
        'active_vehicles_count': active_rentals,
        'recent_activities': recent_activities,
        'vehicles': vehicles,
    }
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_admin)
def admin_vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by('-id')
    return render(request, 'admin/vehicles.html', {'vehicles': vehicles})

@user_passes_test(is_admin)
def admin_vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save() 
            messages.success(request, f"Đã thêm xe {vehicle.name} thành công!")
            return redirect('frontend:admin_vehicles')
        else:
            messages.error(request, "Vui lòng kiểm tra lại các trường dữ liệu nhập vào.")
    else:
        form = VehicleForm()
    return render(request, 'admin/vehicle_form.html', {'form': form, 'title': 'Thêm xe mới'})

@user_passes_test(is_admin)
def admin_vehicle_edit(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f"Đã cập nhật thông tin xe {vehicle.name} thành công!")
            return redirect('frontend:admin_vehicles')
    else:
        form = VehicleForm(instance=vehicle)
    
    return render(request, 'admin/vehicle_form.html', {
        'form': form, 
        'title': f'Chỉnh sửa: {vehicle.name}',
        'vehicle': vehicle
    })

@user_passes_test(is_admin)
def admin_vehicle_delete(request, vehicle_id):
    if request.method == 'POST':
        try:
            vehicle = get_object_or_404(Vehicle, id=vehicle_id)
            vehicle_name = vehicle.name
            vehicle.delete()
            return JsonResponse({'status': 'success', 'message': f'Đã xóa xe {vehicle_name}!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ'}, status=405)

@user_passes_test(is_admin)
def admin_booking_list(request):
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'admin/bookings.html', {'bookings': bookings})

@user_passes_test(is_admin)
def admin_stats(request):
    total_completed = Booking.objects.filter(status='completed').count()
    total_cancelled = Booking.objects.filter(status='cancelled').count()
    current_year = datetime.now().year
    monthly_revenue_data = Booking.objects.filter(
        status='completed', start_date__year=current_year
    ).annotate(month=ExtractMonth('start_date')).values('month').annotate(total=Sum('total_price')).order_by('month')

    revenue_list = [0] * 12
    for entry in monthly_revenue_data:
        revenue_list[entry['month'] - 1] = float(entry['total'])

    context = {
        'total_completed': total_completed,
        'total_cancelled': total_cancelled,
        'revenue_list': revenue_list,
    }
    return render(request, 'admin/analytics.html', context)

# --- TÁC VỤ QUẢN TRỊ NHANH ---

@user_passes_test(is_admin)
def approve_order(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'approved'
    booking.vehicle.status = 'Booked'
    booking.vehicle.save()
    booking.save() 
    messages.success(request, f"Đã phê duyệt đơn hàng cho xe {booking.vehicle.name}")
    return redirect('frontend:admin_dashboard')

@user_passes_test(is_admin)
def admin_release_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.status = 'Available'
    vehicle.save()
    messages.success(request, f"Đã mở trạng thái cho xe {vehicle.name} thành 'Có sẵn'.")
    return redirect('frontend:admin_vehicles')

@user_passes_test(is_admin)
def update_vehicle_location(request):
    if request.method == 'POST':
        v_id = request.POST.get('vehicle_id')
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        vehicle = get_object_or_404(Vehicle, id=v_id)
        vehicle.latitude = float(lat)
        vehicle.longitude = float(lng)
        vehicle.save() 
        messages.success(request, f"Đã cập nhật tọa độ cho xe {vehicle.name}")
    return redirect('frontend:admin_dashboard')

# ==========================================
# 4. AUTH VIEWS (ĐĂNG NHẬP / ĐĂNG KÝ)
# ==========================================

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                messages.success(request, f"Chào mừng Admin {user.username}!")
                return redirect('frontend:admin_dashboard')
            else:
                return redirect('frontend:home')
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
    else:
        form = UserLoginForm()
    return render(request, 'auth/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.")
                return redirect('frontend:login')
            except Exception as e:
                messages.error(request, f"Lỗi đăng ký: {e}")
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('frontend:home')