import os
from .base import *

environment = os.getenv('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if 'development' in environment:
    from .development import *
elif 'production' in environment:
    from .production import *
elif 'testing' in environment:
    from .testing import *
