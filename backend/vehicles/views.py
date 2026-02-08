from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.serializers.json import DjangoJSONEncoder
import json
import random 

from .models import Vehicle, VehicleImage
from bookings.models import Booking
from .forms import ReviewForm, VehicleImageForm
from reviews.models import Review

# ============== 1. API LIST & DETAIL ==============

@require_GET
def vehicle_list_api(request):
    """API: Lấy danh sách xe (Có lọc, phân trang VÀ tọa độ cho Map)"""
    vehicles = Vehicle.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    
    # --- LOGIC LỌC ---
    availability = request.GET.get('availability')
    if availability == 'available':
        vehicles = vehicles.filter(status='available') 
    elif availability == 'unavailable':
        vehicles = vehicles.exclude(status='available')
    
    # Lọc theo giá
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        vehicles = vehicles.filter(price_per_day__gte=min_price)
    if max_price:
        vehicles = vehicles.filter(price_per_day__lte=max_price)
    
    # Sắp xếp
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        vehicles = vehicles.order_by('price_per_day')
    elif sort_by == 'price_desc':
        vehicles = vehicles.order_by('-price_per_day')
    elif sort_by == 'rating':
        vehicles = vehicles.order_by('-avg_rating')
    else:
        vehicles = vehicles.order_by('name')
    
    # Phân trang
    page = request.GET.get('page', 1)
    paginator = Paginator(vehicles, 9)
    page_obj = paginator.get_page(page)
    
    # --- TRẢ VỀ JSON ---
    data = {
        'vehicles': [
            {
                'id': v.id,
                'name': v.name,
                'license_plate': v.license_plate, # Thêm biển số
                'price_per_day': float(v.price_per_day),
                'image': v.image.url if v.image else None,
                'status': v.status, # Dùng status chuẩn
                'avg_rating': round(v.avg_rating, 1) if v.avg_rating else None,
                'review_count': v.review_count,
                # Thêm tọa độ cho Map
                'lat': float(v.latitude) if v.latitude else None,
                'lng': float(v.longitude) if v.longitude else None,
            }
            for v in page_obj
        ],
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    }
    return JsonResponse(data)


@require_GET
def vehicle_detail_api(request, pk):
    """API: Lấy chi tiết xe, ảnh và đánh giá"""
    vehicle = get_object_or_404(
        Vehicle.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ),
        pk=pk
    )
    
    images = vehicle.images.all()
    reviews = vehicle.reviews.select_related('user').order_by('-created_at')
    
    data = {
        'vehicle': {
            'id': vehicle.id,
            'name': vehicle.name,
            'license_plate': vehicle.license_plate,
            'price_per_day': float(vehicle.price_per_day),
            'image': vehicle.image.url if vehicle.image else None,
            'status': vehicle.status,
            'avg_rating': round(vehicle.avg_rating, 1) if vehicle.avg_rating else None,
            'review_count': vehicle.review_count,
            'description': vehicle.description,
            'lat': float(vehicle.latitude) if vehicle.latitude else None,
            'lng': float(vehicle.longitude) if vehicle.longitude else None,
        },
        'images': [{'id': img.id, 'url': img.image.url} for img in images],
        'reviews': [
            {
                'id': r.id,
                'user': r.user.username,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at.isoformat(),
            }
            for r in reviews
        ]
    }
    return JsonResponse(data)


# ============== 2. MAP VIEW ==============

def map_view(request):
    """
    Render trang bản đồ với dữ liệu chuẩn Rental (Rating, Lượt thuê, Giá)
    """
    # Lấy xe có tọa độ + Tính toán Rating trung bình
    vehicles = Vehicle.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    
    vehicles_list = []
    
    for v in vehicles:
        # Xử lý trạng thái hiển thị
        status_display = v.status
        if status_display == 'in_use':
            status_display = 'in operation'
            
        # 1. Rating giả lập 
        rating_val = round(v.avg_rating, 1) if v.avg_rating else 5.0
        
        # 2. Số lượt thuê giả lập 
        trips_val = v.review_count * 15 + random.randint(5, 50)

        vehicles_list.append({
            'id': v.id,
            'name': v.name,
            'plate': v.license_plate,
            'lat': float(v.latitude),
            'lng': float(v.longitude),
            'status': status_display, 
            'price': float(v.price_per_day),
            
            # --- CÁC TRƯỜNG MỚI ---
            'rating': rating_val,
            'trips': trips_val, 
        })

    context = {
        'vehicles_json': json.dumps(vehicles_list, cls=DjangoJSONEncoder)
    }
    return render(request, 'vehicles/map.html', context)


# ============== 3. API REVIEWS & UPLOAD ==============

@login_required
def add_review(request, vehicle_pk):
    """API: Thêm hoặc cập nhật đánh giá"""
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)

    # Kiểm tra user đã có booking completed cho xe này chưa
    has_completed_booking = Booking.objects.filter(
        customer=request.user,
        vehicle=vehicle,
        status='completed'
    ).exists()
    if not has_completed_booking:
        return JsonResponse(
            {'success': False, 'message': 'Bạn cần hoàn thành chuyến đi trước khi đánh giá.'},
            status=403
        )
    existing_review = Review.objects.filter(vehicle=vehicle, user=request.user).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.vehicle = vehicle
            review.user = request.user
            review.save()
            return JsonResponse({
                'success': True, 
                'message': 'Đã cập nhật đánh giá!' if existing_review else 'Cảm ơn bạn đã đánh giá!'
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    if existing_review:
        return JsonResponse({
            'has_review': True,
            'review': {'rating': existing_review.rating, 'comment': existing_review.comment}
        })
    return JsonResponse({'has_review': False})


@login_required
@require_POST
def delete_review(request, review_pk):
    """API: Xóa đánh giá"""
    review = get_object_or_404(Review, pk=review_pk, user=request.user)
    vehicle_pk = review.vehicle.pk
    review.delete()
    return JsonResponse({'success': True, 'message': 'Đã xóa đánh giá!', 'vehicle_id': vehicle_pk})


@login_required
def upload_images(request, vehicle_pk):
    """API: Upload nhiều ảnh"""
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        if not images:
            return JsonResponse({'success': False, 'message': 'Chưa chọn ảnh.'}, status=400)
        
        uploaded = []
        for image in images:
            if image.size > 5 * 1024 * 1024: continue # Skip ảnh > 5MB
            vehicle_image = VehicleImage.objects.create(vehicle=vehicle, image=image)
            uploaded.append({'id': vehicle_image.id, 'url': vehicle_image.image.url})
        
        return JsonResponse({'success': True, 'message': f'Đã upload {len(uploaded)} ảnh!', 'uploaded': uploaded})
    
    images = vehicle.images.all()
    return JsonResponse({
        'vehicle_id': vehicle.pk,
        'images': [{'id': img.id, 'url': img.image.url} for img in images]
    })


@login_required
@require_POST
def delete_image(request, image_pk):
    image = get_object_or_404(VehicleImage, pk=image_pk)
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Quyền hạn bị từ chối.'}, status=403)
    image.image.delete()
    image.delete()
    return JsonResponse({'success': True, 'message': 'Đã xóa ảnh!'})


@require_GET
def get_vehicle_rating(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk)
    stats = vehicle.reviews.aggregate(avg_rating=Avg('rating'), review_count=Count('id'))
    return JsonResponse({
        'avg_rating': round(stats['avg_rating'], 1) if stats['avg_rating'] else 0,
        'review_count': stats['review_count']
    })