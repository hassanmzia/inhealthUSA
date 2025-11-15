"""
IoT Device API URL Configuration

REST API endpoints for IoT device communication.
"""

from django.urls import path
from .api_views import (
    DeviceAuthView,
    PostVitalSignsView,
    BulkPostVitalSignsView,
    PostGlucoseDataView,
    UpdateDeviceStatusView,
    DeviceInfoView,
)

app_name = 'device_api'

urlpatterns = [
    # Authentication
    path('v1/device/auth', DeviceAuthView.as_view(), name='device_auth'),

    # Device Information
    path('v1/device/info', DeviceInfoView.as_view(), name='device_info'),
    path('v1/device/status', UpdateDeviceStatusView.as_view(), name='device_status'),

    # Vital Signs Data
    path('v1/device/vitals', PostVitalSignsView.as_view(), name='post_vitals'),
    path('v1/device/vitals/bulk', BulkPostVitalSignsView.as_view(), name='post_vitals_bulk'),

    # Specialized Data Types
    path('v1/device/glucose', PostGlucoseDataView.as_view(), name='post_glucose'),

    # Future endpoints (placeholders)
    # path('v1/device/ecg', PostECGDataView.as_view(), name='post_ecg'),
    # path('v1/device/activity', PostActivityDataView.as_view(), name='post_activity'),
    # path('v1/device/sleep', PostSleepDataView.as_view(), name='post_sleep'),
]
