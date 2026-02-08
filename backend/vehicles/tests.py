from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
import json
from PIL import Image
import io

from .models import Vehicle, Review, VehicleImage
from .forms import ReviewForm, VehicleImageForm, MultipleImageUploadForm


class VehicleModelTest(TestCase):
    """Test cho Vehicle Model"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.vehicle = Vehicle.objects.create(
            name="Toyota Camry 2024",
            price_per_day=1000000,
            is_available=True
        )
    
    def test_vehicle_creation(self):
        """Test tạo xe mới"""
        self.assertEqual(self.vehicle.name, "Toyota Camry 2024")
        self.assertEqual(self.vehicle.price_per_day, 1000000)
        self.assertTrue(self.vehicle.is_available)
    
    def test_vehicle_str(self):
        """Test __str__ method"""
        self.assertEqual(str(self.vehicle), "Toyota Camry 2024")
    
    def test_vehicle_default_availability(self):
        """Test trạng thái mặc định là sẵn sàng"""
        vehicle = Vehicle.objects.create(
            name="Honda Civic",
            price_per_day=800000
        )
        self.assertTrue(vehicle.is_available)


class ReviewModelTest(TestCase):
    """Test cho Review Model"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            name="Toyota Camry 2024",
            price_per_day=1000000
        )
        self.review = Review.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            rating=5,
            comment="Xe rất tốt!"
        )
    
    def test_review_creation(self):
        """Test tạo review"""
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, "Xe rất tốt!")
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.vehicle, self.vehicle)
    
    def test_review_str(self):
        """Test __str__ method"""
        expected = f"{self.user.username} đánh giá {self.vehicle.name}"
        self.assertEqual(str(self.review), expected)
    
    def test_review_rating_choices(self):
        """Test các lựa chọn rating"""
        valid_ratings = [1, 2, 3, 4, 5]
        for rating in valid_ratings:
            review = Review.objects.create(
                vehicle=self.vehicle,
                user=self.user,
                rating=rating
            )
            self.assertEqual(review.rating, rating)
    
    def test_review_related_name(self):
        """Test related_name hoạt động"""
        self.assertIn(self.review, self.vehicle.reviews.all())


class VehicleImageModelTest(TestCase):
    """Test cho VehicleImage Model"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.vehicle = Vehicle.objects.create(
            name="Toyota Camry 2024",
            price_per_day=1000000
        )
    
    def test_vehicle_image_str(self):
        """Test __str__ method"""
        # Tạo image giả
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x89\x61',  # Fake image content
            content_type='image/jpeg'
        )
        vehicle_image = VehicleImage.objects.create(
            vehicle=self.vehicle,
            image=image
        )
        expected = f"Ảnh của xe {self.vehicle.name}"
        self.assertEqual(str(vehicle_image), expected)


class ReviewFormTest(TestCase):
    """Test cho ReviewForm"""
    
    def test_valid_review_form(self):
        """Test form hợp lệ"""
        form_data = {
            'rating': 5,
            'comment': 'Xe tuyệt vời!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_review_form_without_comment(self):
        """Test form không có comment vẫn hợp lệ"""
        form_data = {
            'rating': 4,
            'comment': ''
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_review_form_without_rating(self):
        """Test form không có rating không hợp lệ"""
        form_data = {
            'comment': 'Test comment'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())


class VehicleListAPITest(TestCase):
    """Test cho Vehicle List API"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.client = Client()
        # Tạo nhiều xe để test
        for i in range(15):
            Vehicle.objects.create(
                name=f"Xe số {i+1}",
                price_per_day=500000 + (i * 100000),
                is_available=(i % 2 == 0)
            )
    
    def test_vehicle_list_api_status_code(self):
        """Test status code 200"""
        response = self.client.get(reverse('vehicles:vehicle_list_api'))
        self.assertEqual(response.status_code, 200)
    
    def test_vehicle_list_api_returns_json(self):
        """Test trả về JSON"""
        response = self.client.get(reverse('vehicles:vehicle_list_api'))
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_vehicle_list_api_pagination(self):
        """Test phân trang hoạt động"""
        response = self.client.get(reverse('vehicles:vehicle_list_api'))
        data = json.loads(response.content)
        self.assertIn('vehicles', data)
        self.assertIn('pagination', data)
        # 9 xe mỗi trang
        self.assertEqual(len(data['vehicles']), 9)
    
    def test_vehicle_list_api_filter_available(self):
        """Test lọc xe sẵn sàng"""
        response = self.client.get(reverse('vehicles:vehicle_list_api'), {'availability': 'available'})
        data = json.loads(response.content)
        for vehicle in data['vehicles']:
            self.assertTrue(vehicle['is_available'])
    
    def test_vehicle_list_api_filter_unavailable(self):
        """Test lọc xe đã thuê"""
        response = self.client.get(reverse('vehicles:vehicle_list_api'), {'availability': 'unavailable'})
        data = json.loads(response.content)
        for vehicle in data['vehicles']:
            self.assertFalse(vehicle['is_available'])


class VehicleDetailAPITest(TestCase):
    """Test cho Vehicle Detail API"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            name="Toyota Camry 2024",
            price_per_day=1000000
        )
        # Tạo review
        Review.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            rating=4,
            comment="Xe tốt"
        )
    
    def test_vehicle_detail_api_status_code(self):
        """Test status code 200"""
        response = self.client.get(
            reverse('vehicles:vehicle_detail_api', kwargs={'pk': self.vehicle.pk})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_vehicle_detail_api_returns_json(self):
        """Test trả về JSON"""
        response = self.client.get(
            reverse('vehicles:vehicle_detail_api', kwargs={'pk': self.vehicle.pk})
        )
        self.assertEqual(response['Content-Type'], 'application/json')
    
    def test_vehicle_detail_api_content(self):
        """Test nội dung trả về"""
        response = self.client.get(
            reverse('vehicles:vehicle_detail_api', kwargs={'pk': self.vehicle.pk})
        )
        data = json.loads(response.content)
        self.assertIn('vehicle', data)
        self.assertIn('images', data)
        self.assertIn('reviews', data)
        self.assertEqual(data['vehicle']['name'], self.vehicle.name)
    
    def test_vehicle_detail_api_404(self):
        """Test 404 khi xe không tồn tại"""
        response = self.client.get(
            reverse('vehicles:vehicle_detail_api', kwargs={'pk': 9999})
        )
        self.assertEqual(response.status_code, 404)


class AddReviewAPITest(TestCase):
    """Test cho Add Review API"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            name="Toyota Camry 2024",
            price_per_day=1000000
        )
    
    def test_add_review_requires_login(self):
        """Test yêu cầu đăng nhập"""
        response = self.client.post(
            reverse('vehicles:add_review', kwargs={'vehicle_pk': self.vehicle.pk}),
            {'rating': 5, 'comment': 'Test'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_add_review_post(self):
        """Test tạo review mới"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('vehicles:add_review', kwargs={'vehicle_pk': self.vehicle.pk}),
            {'rating': 5, 'comment': 'Xe rất tuyệt vời!'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kiểm tra review đã được tạo
        review = Review.objects.filter(vehicle=self.vehicle, user=self.user).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
    
    def test_update_existing_review(self):
        """Test cập nhật review đã tồn tại"""
        self.client.login(username='testuser', password='testpass123')
        
        # Tạo review đầu tiên
        Review.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            rating=3,
            comment="Tạm được"
        )
        
        # Cập nhật review
        response = self.client.post(
            reverse('vehicles:add_review', kwargs={'vehicle_pk': self.vehicle.pk}),
            {'rating': 5, 'comment': 'Đã thay đổi ý kiến!'}
        )
        
        # Kiểm tra chỉ có 1 review
        reviews = Review.objects.filter(vehicle=self.vehicle, user=self.user)
        self.assertEqual(reviews.count(), 1)
        
        # Kiểm tra review đã được cập nhật
        review = reviews.first()
        self.assertEqual(review.rating, 5)


class DeleteReviewAPITest(TestCase):
    """Test cho Delete Review API"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            name="Toyota Camry 2024",
            price_per_day=1000000
        )
        self.review = Review.objects.create(
            vehicle=self.vehicle,
            user=self.user,
            rating=5,
            comment="Test review"
        )
    
    def test_delete_own_review(self):
        """Test xóa review của chính mình"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('vehicles:delete_review', kwargs={'review_pk': self.review.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Kiểm tra review đã bị xóa
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())
    
    def test_cannot_delete_others_review(self):
        """Test không thể xóa review của người khác"""
        self.client.login(username='otheruser', password='testpass123')
        response = self.client.post(
            reverse('vehicles:delete_review', kwargs={'review_pk': self.review.pk})
        )
        self.assertEqual(response.status_code, 404)
        
        # Kiểm tra review vẫn tồn tại
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())


class GetVehicleRatingAPITest(TestCase):
    """Test cho API Rating"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.client = Client()
        self.vehicle = Vehicle.objects.create(
            name="Toyota Camry 2024",
            price_per_day=1000000
        )
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        
        # Tạo reviews
        Review.objects.create(vehicle=self.vehicle, user=self.user1, rating=4)
        Review.objects.create(vehicle=self.vehicle, user=self.user2, rating=5)
    
    def test_get_rating_api(self):
        """Test API trả về đúng dữ liệu"""
        response = self.client.get(
            reverse('vehicles:get_vehicle_rating', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['review_count'], 2)
        self.assertEqual(data['avg_rating'], 4.5)  # (4+5)/2 = 4.5
    
    def test_rating_api_no_reviews(self):
        """Test API khi không có review"""
        new_vehicle = Vehicle.objects.create(
            name="Xe mới",
            price_per_day=500000
        )
        response = self.client.get(
            reverse('vehicles:get_vehicle_rating', kwargs={'vehicle_pk': new_vehicle.pk})
        )
        
        data = json.loads(response.content)
        self.assertEqual(data['review_count'], 0)
        self.assertEqual(data['avg_rating'], 0)


class UploadImagesAPITest(TestCase):
    """Test cho Upload Images API"""
    
    def setUp(self):
        """Tạo dữ liệu test"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='testpass123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='normaluser',
            password='testpass123'
        )
        self.vehicle = Vehicle.objects.create(
            name="Toyota Camry 2024",
            price_per_day=1000000
        )
    
    def test_upload_images_requires_login(self):
        """Test yêu cầu đăng nhập"""
        response = self.client.get(
            reverse('vehicles:upload_images', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertEqual(response.status_code, 302)
    
    def test_upload_images_get(self):
        """Test GET trả về danh sách ảnh hiện tại"""
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get(
            reverse('vehicles:upload_images', kwargs={'vehicle_pk': self.vehicle.pk})
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['vehicle_id'], self.vehicle.pk)
        self.assertIn('images', data)
    
    def create_test_image(self):
        """Helper để tạo ảnh test"""
        image = Image.new('RGB', (100, 100), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        return SimpleUploadedFile(
            name='test.jpg',
            content=image_io.read(),
            content_type='image/jpeg'
        )
    
    def test_upload_single_image(self):
        """Test upload một ảnh"""
        self.client.login(username='staffuser', password='testpass123')
        
        test_image = self.create_test_image()
        
        response = self.client.post(
            reverse('vehicles:upload_images', kwargs={'vehicle_pk': self.vehicle.pk}),
            {'images': test_image},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(self.vehicle.images.count(), 1)


class MultipleImageUploadFormTest(TestCase):
    """Test cho MultipleImageUploadForm"""
    
    def test_form_fields(self):
        """Test form có đúng fields"""
        form = MultipleImageUploadForm()
        self.assertIn('images', form.fields)