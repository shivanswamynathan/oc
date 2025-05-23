import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '-[k~s|hr>Zo3KXQ3&]RQul1azXUgZJ\'pp;2[6en{*Ws*wgN[!4')

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

ALLOWED_HOSTS = ["*", "localhost"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'resume_processor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'resume_enhancer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'resume_enhancer.wsgi.application'
ASGI_APPLICATION = 'resume_enhancer.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development only
MODEL_NAME = os.getenv('MODEL_NAME')



# MongoDB Settings
environment = os.getenv('NODE_ENV', 'development').lower()

if environment == 'production':
    MONGODB_URI = os.getenv('MONGODB_URL_PRODUCTION')
elif environment == 'test':
    MONGODB_URI = os.getenv('MONGODB_URL_TEST')
else:
    MONGODB_URI = os.getenv('MONGODB_URL_DEVELOPMENT')

# Default to development if no connection string is found
if not MONGODB_URI:
    MONGODB_URI = os.getenv('MONGODB_URL_DEVELOPMENT')
    environment = 'development'
    
# Extract database name from connection string or use default
if '/' in MONGODB_URI:
    MONGODB_NAME = MONGODB_URI.split('/')[-1].split('?')[0]
else:
    MONGODB_NAME = 'optimized_cv_dev'
