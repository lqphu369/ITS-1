# FILE: reviews/models.py
from django.db import models
from users.models import User
# Import model Vehicle từ app vehicles sang
from vehicles.models import Vehicle 

class Review(models.Model):
    # Liên kết với Vehicle
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reviews', verbose_name="Xe")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người dùng")
    
    RATING_CHOICES = [
        (1, '1 Sao - Tệ'),
        (2, '2 Sao - Kém'),
        (3, '3 Sao - Bình thường'),
        (4, '4 Sao - Tốt'),
        (5, '5 Sao - Tuyệt vời'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, default=5, verbose_name="Điểm đánh giá")
    comment = models.TextField(blank=True, null=True, verbose_name="Nhận xét")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.user.username} đánh giá {self.vehicle.name}"