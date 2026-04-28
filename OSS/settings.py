import os
import environ
from pathlib import Path
from decouple import config


env = environ.Env(
    DEBUG=(bool, False)
)
ALLOWED_HOSTS = ['*']
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))
else:
    print(f"⚠️ Cảnh báo: Không tìm thấy file .env tại {env_file}")
if os.name == 'nt':
    # Đường dẫn chuẩn lấy từ ảnh image_1761b4.jpg của bạn
    OSGEO4W_BIN = env('OSGEO4W')






if os.name == 'nt':
    OSGEO4W_BIN = env('OSGEO4W')
    if os.path.exists(OSGEO4W_BIN):
        os.environ['PATH'] = OSGEO4W_BIN + os.path.pathsep + os.environ['PATH']
        # 2. Quan trọng cho Python 3.8+: Nạp thư mục DLL
        os.add_dll_directory(OSGEO4W_BIN)

        # 3. Chỉ định đích danh thư viện (Khớp với image_1761b4.jpg)
        GDAL_LIBRARY_PATH = os.path.join(OSGEO4W_BIN, 'gdal312.dll')
        GEOS_LIBRARY_PATH = os.path.join(OSGEO4W_BIN, 'geos_c.dll')

        # 4. Thêm thư viện PROJ (cần thiết cho tọa độ)
        os.environ['PROJ_LIB'] = os.path.join(Path(OSGEO4W_BIN).parent, 'share', 'proj')
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy thư mục OSGeo4W tại {OSGEO4W_BIN}")
# -----------------------------------------------


SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
# 3. ĐĂNG KÝ CÁC ỨNG DỤNG
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',      
     'GISDjango',
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


ROOT_URLCONF = 'GISDjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'GISDjango' / 'view'],
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

WSGI_APPLICATION = 'GISDjango.router.wsgi.application'
ASGI_APPLICATION = 'GISDjango.router.asgi.application'

# 4. CẤU HÌNH DATABASE (Sử dụng PostGIS cho GIS-Ecommerce)
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

# 6. FILE TĨNH (CSS, JS, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / "node_modules",    
]
STATIC_ROOT = BASE_DIR.parent / "static"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# # 7. FIX LỖI GDAL TRÊN WINDOWS (Cho Python 3.13)
# if os.name == 'nt':
#     OSGEO4W_ROOT = r'C:\OSGeo4W'
#     osgeo_bin = os.path.join(OSGEO4W_ROOT, 'bin')
#
#     if os.path.exists(osgeo_bin):
#         # Hỗ trợ Python 3.13 nạp DLL từ OSGeo4W
#         os.add_dll_directory(osgeo_bin)
#         os.environ['PATH'] = osgeo_bin + os.pathsep + os.environ['PATH']
#
#     os.environ['PROJ_LIB'] = os.path.join(OSGEO4W_ROOT, 'share', 'proj')
#
#     # Thịnh kiểm tra lại chính xác file dll trong C:\OSGeo4W\bin của bạn
#     GDAL_LIBRARY_PATH = os.path.join(osgeo_bin, 'gdal312.dll')
#     GEOS_LIBRARY_PATH = os.path.join(osgeo_bin, 'geos_c.dll')

CART_SESSION_ID = 'cart'
AUTH_USER_MODEL = 'GISDjango.User'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER = '9c2f68037e1de9'
EMAIL_HOST_PASSWORD = 'bf6f68313ef7f5'
EMAIL_PORT = 2525 

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'test@example.com'

