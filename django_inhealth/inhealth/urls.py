"""
URL configuration for InHealth EHR project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from healthcare import saml_views

# Customize Django Admin Site
admin.site.site_header = "InHealth EHR Administration"
admin.site.site_title = "InHealth EHR Admin"
admin.site.index_title = "InHealth EHR Administration"

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django-allauth URLs (social authentication)
    path('accounts/', include('allauth.urls')),

    # Mozilla Django OIDC URLs (Azure AD, Okta, AWS Cognito)
    path('oidc/', include('mozilla_django_oidc.urls')),

    # SAML URLs
    path('saml/login/', saml_views.saml_login, name='saml_login'),
    path('saml/acs/', saml_views.saml_acs, name='saml_acs'),
    path('saml/metadata/', saml_views.saml_metadata, name='saml_metadata'),
    path('saml/sls/', saml_views.saml_sls, name='saml_sls'),

    # Healthcare app URLs
    path('', include('healthcare.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
