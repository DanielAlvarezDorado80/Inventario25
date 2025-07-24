# wsgi.py placeholder
import os
from django.core.wsgi import get_wsgi_application

environment = os.getenv('DJANGO_ENV', 'dev')  # 'dev' por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'Inventario25.settings.{environment}')

application = get_wsgi_application()





