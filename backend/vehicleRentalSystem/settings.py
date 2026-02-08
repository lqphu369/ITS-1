from pathlib import Path
import os
import sys
import dj_database_url

# Định nghĩa thư mục gốc (Trỏ đến thư mục chứa manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Thêm BASE_DIR vào hệ thống để Django nhận diện các app
sys.path.append(str(BASE_DIR))

# 2. Cấu hình Bảo mật
SECRET_KEY = 'django-insecure-^u30-jmlkmxhizxcva5*vy56kj)3beu^n%e%u!z8yfr60tv*ae'

# Trên Render, DEBUG sẽ là False (an toàn). Ở nhà, nó là True (để sửa lỗi).
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['*'] # Cho phép truy cập từ mọi host trong Docker

# 3. Đăng ký các ứng dụng
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'users',      
    'bookings',   
    'vehicles',   
    'reviews',   
    'frontend',   
]

# 4. Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vehicleRentalSystem.urls'

# 5. Cấu hình Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR  / 'frontend' / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vehicleRentalSystem.wsgi.application'

# 6. Database (PostgreSQL qua Docker)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vehicle_rental_system',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

# Ghi đè cấu hình nếu đang chạy trên Render
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)

# 8. Ngôn ngữ và Thời gian
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# 9. Static files (CSS, JS)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "static", 
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Cấu hình nén file tĩnh cho WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 10. Media files (CẤU HÌNH QUAN TRỌNG ĐỂ HIỆN ẢNH)
# URL để truy cập ảnh từ trình duyệt (ví dụ: http://localhost:8000/media/car.jpg)
MEDIA_URL = '/media/'
# Đường dẫn vật lý để Django lưu ảnh vào thư mục media trong dự án
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'