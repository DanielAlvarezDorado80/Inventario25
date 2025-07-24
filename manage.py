# manage.py placeholder
#!/usr/bin/env python
# Script principal para gestionar tareas administrativas del proyecto Django Inventario25

import os
import sys
import logging

def main():
    environment = os.getenv('DJANGO_ENV', 'dev').lower()
    VALID_ENVS = ('dev', 'prod', 'staging')

    if environment not in VALID_ENVS:
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Error: entorno inválido '{environment}'. Usa uno de: {VALID_ENVS}")
        print(f"Error: entorno inválido '{environment}'. Usa uno de: {VALID_ENVS}")
        sys.exit(1)

    settings_module = f'Inventario25.settings.{environment}'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

    # Configura logging según entorno
    if not logging.getLogger().hasHandlers():
        level = logging.DEBUG if environment == 'dev' else logging.INFO
        logging.basicConfig(level=level)

    logging.debug(f"Usando configuración: {settings_module}")

    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
    except ImportError:
        logging.exception("No se puede importar Django. Activa el entorno virtual e instala Django.")
        sys.exit(1)
    except Exception:
        logging.exception("Error inesperado al ejecutar manage.py")
        sys.exit(1)

if __name__ == '__main__':
    main()
