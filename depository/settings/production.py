from .base import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': get_env_var('DB_PATH', default=os.path.join('/home/khat/db/db.sqlite3')),  # NOQA
    }
}
DEBUG = False
