"""
URL configuration for InHealth EHR project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Customize Django Admin Site
admin.site.site_header = "InHealth EHR Administration"
admin.site.site_title = "InHealth EHR Admin"
admin.site.index_title = "InHealth EHR Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('healthcare.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
