import os
from datetime import timedelta

import environ
from pathlib import Path

env = environ.Env(
    DEBUG=(bool, False)
)

ALLOWED_HOSTS = ['*']
BASE_DIR = Path(__file__).resolve().parent.parent

# Đọc file .env
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))
else:
    print(f"⚠️ Cảnh báo: Không tìm thấy file .env tại {env_file}")

# Nạp thư viện GDAL cho GIS
if os.name == 'nt':
    OSGEO4W_BIN = env('OSGEO4W')
    if os.path.exists(OSGEO4W_BIN):
        os.environ['PATH'] = OSGEO4W_BIN + os.pathsep + os.environ['PATH']
        # Quan trọng cho Python 3.8+: Nạp thư mục DLL
        os.add_dll_directory(OSGEO4W_BIN)

        # Chỉ định đích danh thư viện
        GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_BIN, 'gdal312.dll')
        GEOS_LIBRARY_PATH = os.path.join(OSGEO4W_BIN, 'geos_c.dll')

        # Thêm thư viện PROJ (cần thiết cho tọa độ)
        os.environ['PROJ_LIB'] = os.path.join(Path(OSGEO4W_BIN).parent, 'share', 'proj')
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy thư mục OSGeo4W tại {OSGEO4W_BIN}")
# -----------------------------------------------

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# ĐĂNG KÝ CÁC ỨNG DỤNG
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',      
    'OSS', 
    'compressor',
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

# Đã đổi từ GISDjango thành OSS
ROOT_URLCONF = 'OSS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'OSS' / 'view'],  # Đã đổi từ GISDjango thành OSS
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

# Đã đổi từ GISDjango thành OSS
WSGI_APPLICATION = 'OSS.wsgi.application'
ASGI_APPLICATION = 'OSS.asgi.application'

# CẤU HÌNH DATABASE (PostGIS)
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

LANGUAGE_CODE = 'vi-vn'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# FILE TĨNH (CSS, JS, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / "node_modules",    
]
STATIC_ROOT = BASE_DIR.parent / "static"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CART_SESSION_ID = 'cart'
AUTH_USER_MODEL = 'OSS.User'  # Đã đổi từ GISDjango thành OSS

# CẤU HÌNH GỬI MAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER = '9c2f68037e1de9'
EMAIL_HOST_PASSWORD = 'bf6f68313ef7f5'
EMAIL_PORT = 2525 
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'test@example.com'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# Cấu hình thời hạn của Token
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Token có hiệu lực trong 1 tiếng
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # Refresh token dùng được trong 1 ngày
    'AUTH_HEADER_TYPES': ('Bearer',),
}