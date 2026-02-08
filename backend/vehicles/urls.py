from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [

    # API: Danh sách xe
    path('api/vehicles/', views.vehicle_list_api, name='vehicle_list_api'),
    
    # API: Chi tiết xe
    path('api/vehicles/<int:pk>/', views.vehicle_detail_api, name='vehicle_detail_api'),
    
    # API: Đánh giá xe
    path('api/vehicles/<int:vehicle_pk>/review/', views.add_review, name='add_review'),
    path('api/reviews/<int:review_pk>/delete/', views.delete_review, name='delete_review'),
    
    # API: Upload ảnh xe
    path('api/vehicles/<int:vehicle_pk>/images/', views.upload_images, name='upload_images'),
    path('api/images/<int:image_pk>/delete/', views.delete_image, name='delete_image'),
    
    # API: Lấy rating của xe
    path('api/vehicles/<int:vehicle_pk>/rating/', views.get_vehicle_rating, name='get_vehicle_rating'),

    path('api/list/', views.vehicle_list_api, name='vehicle_list_api'),
    path('map/', views.map_view, name='map'),
]

