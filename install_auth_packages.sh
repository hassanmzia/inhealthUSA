#!/bin/bash
# Installation script for InHealth EHR Enterprise Authentication packages

set -e  # Exit on error

echo "=========================================="
echo "InHealth EHR - Enterprise Authentication"
echo "Package Installation Script"
echo "=========================================="
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "WARNING: No virtual environment detected!"
    echo "It's recommended to activate your virtual environment first:"
    echo "  source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
fi

echo "Installing packages from requirements.txt..."
echo ""

# Install packages
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy environment template:"
echo "   cp .env.django.example .env"
echo ""
echo "2. Edit .env with your configuration"
echo ""
echo "3. Run database migrations:"
echo "   cd django_inhealth"
echo "   python manage.py migrate"
echo ""
echo "4. Create Site object:"
echo "   python manage.py shell"
echo "   >>> from django.contrib.sites.models import Site"
echo "   >>> site = Site.objects.get(id=1)"
echo "   >>> site.domain = 'localhost:8000'"
echo "   >>> site.name = 'InHealth EHR'"
echo "   >>> site.save()"
echo "   >>> exit()"
echo ""
echo "5. Read the setup guide:"
echo "   See ENTERPRISE_AUTH_SETUP.md for provider configuration"
echo ""
