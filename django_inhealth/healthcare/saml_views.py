"""
SAML 2.0 Authentication Views
Handles SAML SSO login, metadata, and callbacks
"""

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from healthcare.auth_backends import SAMLAuthBackend
import logging

logger = logging.getLogger(__name__)


def init_saml_auth(request):
    """
    Initialize SAML authentication
    """
    auth = OneLogin_Saml2_Auth(request, custom_base_path=get_saml_settings())
    return auth


def get_saml_settings():
    """
    Get SAML configuration from Django settings
    """
    # Build SAML configuration dict
    saml_settings = {
        'strict': True,
        'debug': settings.DEBUG,
        'sp': {
            'entityId': settings.SAML_SP_ENTITY_ID,
            'assertionConsumerService': {
                'url': settings.SAML_SP_ACS_URL,
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
            },
            'singleLogoutService': {
                'url': settings.SAML_SP_SLS_URL,
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
            'x509cert': '',
            'privateKey': ''
        },
        'idp': {
            'entityId': settings.SAML_IDP_ENTITY_ID,
            'singleSignOnService': {
                'url': settings.SAML_IDP_SSO_URL,
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'singleLogoutService': {
                'url': '',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'x509cert': settings.SAML_IDP_X509_CERT
        }
    }

    return saml_settings


def prepare_django_request(request):
    """
    Prepare Django request for SAML library
    """
    result = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    return result


@require_http_methods(['GET'])
def saml_login(request):
    """
    Initiate SAML SSO login
    """
    if not getattr(settings, 'SAML_ENABLED', False):
        return HttpResponse('SAML authentication is not enabled', status=400)

    try:
        req = prepare_django_request(request)
        auth = OneLogin_Saml2_Auth(req, get_saml_settings())

        # Store intended destination
        return_to = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        request.session['saml_return_to'] = return_to

        # Initiate SAML login
        sso_url = auth.login(return_to=return_to)
        request.session['auth_provider'] = 'saml'

        return HttpResponseRedirect(sso_url)

    except Exception as e:
        logger.error(f'SAML login error: {str(e)}')
        return HttpResponse(f'SAML login error: {str(e)}', status=500)


@csrf_exempt
@require_http_methods(['POST'])
def saml_acs(request):
    """
    SAML Assertion Consumer Service
    Handles SAML response from IdP
    """
    if not getattr(settings, 'SAML_ENABLED', False):
        return HttpResponse('SAML authentication is not enabled', status=400)

    try:
        req = prepare_django_request(request)
        auth = OneLogin_Saml2_Auth(req, get_saml_settings())

        # Process SAML response
        auth.process_response()

        errors = auth.get_errors()
        if errors:
            logger.error(f'SAML ACS errors: {", ".join(errors)}')
            return HttpResponse(f'SAML errors: {", ".join(errors)}', status=400)

        if not auth.is_authenticated():
            logger.warning('SAML authentication failed')
            return HttpResponse('SAML authentication failed', status=401)

        # Get SAML attributes
        saml_attributes = auth.get_attributes()
        saml_nameid = auth.get_nameid()

        logger.info(f'SAML authentication successful for: {saml_nameid}')

        # Authenticate user via SAML backend
        backend = SAMLAuthBackend()
        user = backend.authenticate(request, saml_attributes=saml_attributes)

        if user:
            # Log user in
            login(request, user, backend='healthcare.auth_backends.SAMLAuthBackend')

            # Get return URL
            return_to = request.session.get('saml_return_to', settings.LOGIN_REDIRECT_URL)

            # Redirect to relay state if provided
            relay_state = request.POST.get('RelayState')
            if relay_state:
                return HttpResponseRedirect(auth.redirect_to(relay_state))

            return HttpResponseRedirect(return_to)
        else:
            logger.error('Failed to authenticate user from SAML attributes')
            return HttpResponse('Authentication failed', status=401)

    except Exception as e:
        logger.error(f'SAML ACS error: {str(e)}')
        return HttpResponse(f'SAML ACS error: {str(e)}', status=500)


@require_http_methods(['GET'])
def saml_metadata(request):
    """
    SAML Service Provider metadata endpoint
    """
    if not getattr(settings, 'SAML_ENABLED', False):
        return HttpResponse('SAML authentication is not enabled', status=400)

    try:
        req = prepare_django_request(request)
        auth = OneLogin_Saml2_Auth(req, get_saml_settings())
        saml_settings = auth.get_settings()

        metadata = saml_settings.get_sp_metadata()
        errors = saml_settings.validate_metadata(metadata)

        if errors:
            logger.error(f'SAML metadata errors: {", ".join(errors)}')
            return HttpResponse(f'SAML metadata errors: {", ".join(errors)}', status=500)

        return HttpResponse(metadata, content_type='text/xml')

    except Exception as e:
        logger.error(f'SAML metadata error: {str(e)}')
        return HttpResponse(f'SAML metadata error: {str(e)}', status=500)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def saml_sls(request):
    """
    SAML Single Logout Service
    """
    if not getattr(settings, 'SAML_ENABLED', False):
        return HttpResponse('SAML authentication is not enabled', status=400)

    try:
        req = prepare_django_request(request)
        auth = OneLogin_Saml2_Auth(req, get_saml_settings())

        url = auth.process_slo()
        errors = auth.get_errors()

        if errors:
            logger.error(f'SAML SLS errors: {", ".join(errors)}')

        if url:
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)

    except Exception as e:
        logger.error(f'SAML SLS error: {str(e)}')
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
