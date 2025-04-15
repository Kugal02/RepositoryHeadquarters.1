from pathlib import Path
import os
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env()
env.read_env(str(BASE_DIR / '.env'))  # Read the .env file

# Retrieve SECRET_KEY from .env file
SECRET_KEY = env('SECRET_KEY')

# Debugging to print the SECRET_KEY and DEBUG after they have been loaded
print("SECRET_KEY:", SECRET_KEY)
print("DEBUG:", env('DEBUG', default=True))

# ALLOWED_HOSTS - Define which host/domain the site can be accessed from.
ALLOWED_HOSTS = [
    'provideragencyportal.com',
    'www.provideragencyportal.com',
    '127.0.0.1',
    'localhost',
    '3.141.164.157',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'agency.apps.AgencyConfig',
    'widget_tweaks',
]

AUTH_USER_MODEL = 'accounts.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'agency.middleware.ClearMessagesOnLogoutMiddleware',
]

ROOT_URLCONF = 'ProviderAgencyPortal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'agency', 'templates'),
        ],
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

WSGI_APPLICATION = 'ProviderAgencyPortal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Use SQLite instead of PostgreSQL
        'NAME': BASE_DIR / 'db.sqlite3',  # SQLite database file location
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "agency" / "static",
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Mailgun API credentials (from environment variables)
MAILGUN_API_KEY = env('MAILGUN_API_KEY')
MAILGUN_DOMAIN = env('MAILGUN_DOMAIN')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

# Other settings
DEBUG = env.bool('DEBUG', default=True)

LOGIN_REDIRECT_URL = '/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = '/login/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
