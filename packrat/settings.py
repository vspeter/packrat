# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vgmxo603zkfltt(3oq(#%eewe=@dr-g$$r-9a_o!oh6@rr3h#m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
)

# Application definition

INSTALLED_APPS = (
    'packrat.Attrib',
    'packrat.Repo',
    'packrat.Package',
    'packrat.Auth',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
)

MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = ''

WSGI_APPLICATION = 'packrat.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/packrat/db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

FILE_UPLOAD_MAX_MEMORY_SIZE = 0


import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MEDIA_URL = '/files/'
MEDIA_ROOT = '/var/www/packrat/api/files'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'www/files') # for Dev work
