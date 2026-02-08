from django import forms
from .models import VehicleImage, Vehicle
from reviews.models import Review

class ReviewForm(forms.ModelForm):
    """Form để người dùng đánh giá xe (Giữ nguyên)"""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-radio'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Nhập nhận xét của bạn về xe này...'
            }),
        }
        labels = {
            'rating': 'Đánh giá',
            'comment': 'Nhận xét',
        }

class VehicleImageForm(forms.ModelForm):
    """Form để upload ảnh xe (Giữ nguyên)"""
    class Meta:
        model = VehicleImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'image': 'Chọn ảnh',
        }

class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget để hỗ trợ upload nhiều file"""
    allow_multiple_selected = True

class MultipleImageUploadForm(forms.Form):
    """Form để upload nhiều ảnh cùng lúc"""
    images = forms.FileField(  # Sửa ImageField thành FileField để tương thích tốt hơn với widget custom
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'multiple': True
        }),
        label='Chọn ảnh (có thể chọn nhiều ảnh)',
        required=False
    )

    def clean_images(self):
        """Validate ảnh được upload"""
        return self.cleaned_data.get('images')

# --- PHẦN QUAN TRỌNG NHẤT CẦN SỬA ---
class VehicleForm(forms.ModelForm):
    """Form để tạo/sửa xe (Đã cập nhật cho Map ITS)"""
    class Meta:
        model = Vehicle
        # Cập nhật danh sách trường khớp với Model mới
        fields = [
            'name', 
            'license_plate',    # Mới
            'vehicle_type',     # Mới
            'price_per_day', 
            'status',           # Thay thế cho is_available
            'image', 
            'description',      # Mới
            'latitude',         # Mới (cho Map)
            'longitude'         # Mới (cho Map)
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên xe'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Biển số (VD: 51H-123.45)'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}), # Dropdown chọn loại xe
            'price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Giá thuê/ngày'}),
            'status': forms.Select(attrs={'class': 'form-select'}),       # Dropdown chọn trạng thái
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả chi tiết về xe...'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Vĩ độ (Latitude)'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Kinh độ (Longitude)'}),
        }
        
        labels = {
            'name': 'Tên xe',
            'license_plate': 'Biển số',
            'vehicle_type': 'Loại xe',
            'price_per_day': 'Giá thuê (VND)',
            'status': 'Trạng thái',
            'image': 'Ảnh đại diện',
            'description': 'Mô tả',
            'latitude': 'Vĩ độ',
            'longitude': 'Kinh độ'
        }