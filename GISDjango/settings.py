import os
from pathlib import Path
from decouple import config

# 1. ĐƯỜNG DẪN GỐC
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. BẢO MẬT (Đọc từ file .env)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key-thinh-2026')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = []

# 3. ĐĂNG KÝ CÁC ỨNG DỤNG
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # Quan trọng cho PostGIS
    'GISDjango',
    'store',               # App bán cây của Thịnh
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GISDjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'GISDjango.wsgi.application'

# 4. CẤU HÌNH DATABASE (Sử dụng PostGIS từ file .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# 5. CÁC CẤU HÌNH KHÁC
LANGUAGE_CODE = 'vi-vn'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 6. FIX LỖI GDAL TRÊN WINDOWS (Dành cho Python 3.13)
if os.name == 'nt':
    OSGEO4W_ROOT = r'C:\OSGeo4W'
    osgeo_bin = os.path.join(OSGEO4W_ROOT, 'bin')
    
    if os.path.exists(osgeo_bin):
        # Quan trọng: add_dll_directory giúp Python 3.13 tìm thấy các file phụ thuộc
        os.add_dll_directory(osgeo_bin)
        os.environ['PATH'] = osgeo_bin + os.pathsep + os.environ['PATH']
    
    os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, 'share', 'proj')
    
    # Kiểm tra kỹ tên file gdal312.dll trong máy bạn
    GDAL_LIBRARY_PATH = os.path.join(osgeo_bin, 'gdal312.dll') 
    GEOS_LIBRARY_PATH = os.path.join(osgeo_bin, 'geos_c.dll')