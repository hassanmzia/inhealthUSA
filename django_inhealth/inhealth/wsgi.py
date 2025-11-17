"""
WSGI config for InHealth EHR project.
"""

import os

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Get the project directory (parent of inhealth directory)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(base_dir, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inhealth.settings')

application = get_wsgi_application()
