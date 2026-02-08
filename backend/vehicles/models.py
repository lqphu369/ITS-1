from django.db import models
from users.models import User 
from datetime import timedelta 

# ============
# 1. MODEL XE 
# ============
class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),       # Đồng bộ chuẩn viết hoa
        ('booked', 'Booked'),             # Đồng bộ chuẩn viết hoa
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
    ]

    VEHICLE_TYPE_CHOICES = [
        ('bike', 'Bike'),
        ('car_4', 'Car 4 seats'),
        ('car_7', 'Car 7 seats'),
    ]

    name = models.CharField(max_length=100)
    
    license_plate = models.CharField(
        max_length=20,
        unique=True
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles',
        null=True, 
        blank=True
    )

    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        default='bike'
    )

    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- TỰ ĐỘNG XÁC ĐỊNH SỐ CHỖ DỰA TRÊN LOẠI XE ---
    @property
    def seats(self):
        """Trả về số lượng chỗ ngồi thực tế dựa trên vehicle_type để hiển thị UI"""
        if self.vehicle_type == 'car_7':
            return 7
        elif self.vehicle_type == 'car_4':
            return 4
        return 2  # Mặc định cho 'bike'

    # --- TỰ ĐỘNG XÁC ĐỊNH NHIÊN LIỆU ---
    @property
    def fuel_display(self):
        """Trả về nhãn nhiên liệu tương ứng với từng loại xe"""
        if self.vehicle_type == 'bike':
            return "Điện/Xăng"
        return "Xăng"

    # --- HÀM TÍNH TỔNG TIỀN: DUYỆT TỪNG NGÀY ĐỂ TÍNH PHỤ PHÍ CHÍNH XÁC ---
    def calculate_total_price(self, pickup_date, return_date):
        """Tính tổng tiền: Từng ngày một + 20% phụ phí nếu rơi vào Thứ 7/CN"""
        if not pickup_date or not return_date:
            return self.price_per_day
            
        delta = return_date - pickup_date
        total_days = delta.days if delta.days > 0 else 1
        
        total_amount = 0
        current_date = pickup_date
        daily_price = float(self.price_per_day)

        # Duyệt qua từng ngày trong khoảng thời gian thuê để kiểm tra cuối tuần
        for i in range(total_days):
            # weekday() trả về 5 cho Thứ 7 và 6 cho Chủ nhật
            if current_date.weekday() >= 5:
                total_amount += daily_price * 1.2  # Áp dụng phụ phí 20% cho ngày này
            else:
                total_amount += daily_price  # Giá ngày thường
            
            # Nhảy sang ngày tiếp theo để kiểm tra
            current_date += timedelta(days=1)
            
        return total_amount

    def __str__(self):
        return f"{self.name} - {self.license_plate}"

# ======================
# 2. MODEL ẢNH CHI TIẾT 
# ======================
class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicle_gallery/', verbose_name="Ảnh chi tiết")

    def __str__(self):
        return f"Ảnh của xe {self.vehicle.name}"