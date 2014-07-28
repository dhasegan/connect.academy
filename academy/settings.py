# Django settings for academy project.

from os import environ, path
import boto

#Authentication Backends
AUTHENTICATION_BACKENDS = ('app.auth.helpers.jUserBackend',)

DEBUG = environ.get('ACADEMY_DEBUG_STATE', 'True') == 'True'
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Daniel Hasegan', 'daniel@hasegan.com'),
)

MANAGERS = ADMINS

PROJECT_ROOT = path.realpath(path.dirname(__file__)) + '/'

DATABASES = {
    'default': {
        'ENGINE': environ.get('ACADEMY_DATABASE_BACKEND', 'django.db.backends.sqlite3'),
        'NAME': environ.get('ACADEMY_DATABASE_NAME', PROJECT_ROOT + 'db/database.db'),
        'USER': environ.get('ACADEMY_DATABASE_USER', ''),
        'PASSWORD': environ.get('ACADEMY_DATABASE_PASSWORD', ''),
        'HOST': environ.get('ACADEMY_DATABASE_HOST', ''),
        'PORT': environ.get('ACADEMY_DATABASE_PORT', ''),
        'TEST_NAME': environ.get('ACADEMY_DATABASE_TEST_NAME', PROJECT_ROOT + 'db/test_database.db'),
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

LOGIN_URL = '/welcome'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = path.join(PROJECT_ROOT, 'staticfiles/')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    path.join(PROJECT_ROOT, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = environ.get('ACADEMY_SECRET_KEY', '^vix^ohv5hl+w9yv(o!1-b#$54vm_p$12s(a7iiz14u*c&gs@1')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "versioning.middleware.VersioningMiddleware",
)

ROOT_URLCONF = 'academy.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'academy.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "app.context_processors.user_authenticated",
    "app.context_processors.debug")

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.humanize',
    'django_extensions', # for special commands
    'pipeline', # js and css/less compilers
    'storages',
    'app',
    'versioning',  # Should be after apps with versioned models
    'south',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

######################## Email settings

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' if not DEBUG else 'django.core.mail.backends.console.EmailBackend'



######################### Media files

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
COURSE_DOCUMENT_MAX_UPLOAD_SIZE = "5242880"

### Development mode

# Library of file storage middleware
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = PROJECT_ROOT + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
MEDIA_URL = '/media/'

### AWS in production

AWS_ACCESS_KEY_ID = environ.get('ACADEMY_AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = environ.get('ACADEMY_AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = 'academy'
AWS_PRELOAD_METADATA = True

# Connect to s3 in production
if not DEBUG:
    boto.connect_s3()
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    MEDIA_URL = 'http://{0}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)

########################## South library configuration

SOUTH_TESTS_MIGRATE = False

########################### Pipeline settings 

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
PIPELINE_JS_COMPRESSOR = "pipeline.compressors.yuglify.YuglifyCompressor" if not DEBUG else None

PIPELINE_COMPILERS = (
  'pipeline.compilers.sass.SASSCompiler',
)

PIPELINE_CSS = {
    'bootstrap': {
        'source_filenames': (
            'bootstrap/stylesheets/bootstrap.scss',
        ),
        'output_filename': 'css/bootstrap.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'connect': {
        'source_filenames': (
          'css/connect.scss',
        ),
        'output_filename': 'css/connect.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
}

PIPELINE_JS = {
    'connect_base': {
        'source_filenames': (
          'js/jcourse.js',
        ),
        'output_filename': 'js/connect_base.min.js',
    },
    'bootstrap': {
        'source_filenames': (
          'bootstrap/javascripts/bootstrap.js',
        ),
        'output_filename': 'js/bootstrap.min.js',
    },
}

########################## Django extension config

SHELL_PLUS_POST_IMPORTS = (
    ('app.models', '*'),
    ('app.populator', '*')
)

########################## Other settings

VALID_TIME_INPUTS = ['%d/%m/%Y %H:%M:%S',    # '25/10/2006 14:30:59'
                    '%d/%m/%Y %H:%M',        # '25/10/2006 14:30'
                    '%d/%m/%Y',              # '25/10/2006'
                    '%d/%m/%y %H:%M:%S',     # '25/10/06 14:30:59'
                    '%d/%m/%y %H:%M',        # '25/10/06 14:30'
                    '%d/%m/%y'               # '25/10/06 14:30'
                    ]

### Forum post rankings settings
# Higher judgement means higher thresholds for merit and age

MERIT_JUDGEMENT = 2
AGE_JUDGEMENT = 300000
