from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

# --- IMPORT MODELS ---
# Sử dụng try-except để đảm bảo an toàn nếu các app chưa được thiết lập hoàn tất
try:
    from reviews.models import Review 
    from vehicles.models import Vehicle
except ImportError:
    Review = None
    Vehicle = None

User = get_user_model()

# ==========================
# 1. FORM ĐĂNG NHẬP
# ==========================
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full pl-11 pr-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-primary',
        'placeholder': 'Tên đăng nhập'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full pl-11 pr-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-primary',
        'placeholder': 'Mật khẩu'
    }))

# ==========================
# 2. FORM ĐĂNG KÝ
# ==========================
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white',
        'placeholder': 'Nhập ít nhất 8 ký tự'
    }))
    confirm_password = forms.CharField(label="Nhập lại mật khẩu", widget=forms.PasswordInput(attrs={
        'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white',
        'placeholder': 'Nhập lại mật khẩu'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'driver_license_image', 'phone_number', 'address'] 
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Mật khẩu xác nhận không khớp.")
        return cleaned_data

# ==========================
# 3. FORM ĐÁNH GIÁ
# ==========================
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review if Review else None
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 
                'max': 5, 
                'class': 'w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white px-3 py-2'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white p-3',
                'placeholder': 'Kể cho chúng tôi về trải nghiệm lái...',
                'rows': '4'
            })
        }

# ==========================
# 4. FORM QUẢN LÝ XE (ADMIN)
# ==========================
class VehicleForm(forms.ModelForm):
    class Meta:
        # Nếu model Vehicle tồn tại thì liên kết, nếu không thì để None để tránh crash
        model = Vehicle if Vehicle else None
        fields = [
            'name', 'license_plate', 'vehicle_type', 
            'price_per_day', 'status', 'image', 
            'latitude', 'longitude'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white', 
                'placeholder': 'Tên xe...'
            }),
            'license_plate': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white', 
                'placeholder': 'Biển số...'
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white'
            }),
            # Load trực tiếp Choice 'Available' từ Model, không ép kiểu
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white'
            }),
            'price_per_day': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white', 
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white', 
                'step': 'any'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg dark:bg-slate-900 dark:text-white'
            }),
        }