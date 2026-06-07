from django.urls import path

from . import views
from . import views_management
from . import views_operations
from . import views_packages
from . import views_reports

app_name = 'ccms_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('branches/', views_management.branch_list, name='branch_list'),
    path('branches/add/', views_management.branch_create, name='branch_create'),
    path('branches/<int:pk>/edit/', views_management.branch_edit, name='branch_edit'),
    path('branches/<int:pk>/toggle-status/', views_management.branch_toggle_status, name='branch_toggle_status'),
    path('vehicles/', views_management.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views_management.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/', views_management.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/edit/', views_management.vehicle_edit, name='vehicle_edit'),
    path('packages/', views_packages.package_list, name='package_list'),
    path('packages/register/', views_packages.package_register, name='package_register'),
    path('packages/<int:pk>/', views_packages.package_detail, name='package_detail'),
    path('packages/<int:pk>/qr/', views_packages.package_qr, name='package_qr'),
    path('packages/<int:pk>/qr.png', views_packages.package_qr_image, name='package_qr_image'),
    path('operations/scan-arrival/', views_operations.scan_arrival, name='scan_arrival'),
    path('operations/scan-arrival/<str:tracking_number>/', views_operations.arrival_confirm, name='arrival_confirm'),
    path('operations/confirm-delivery/', views_operations.confirm_delivery_lookup, name='confirm_delivery_lookup'),
    path('operations/confirm-delivery/<str:tracking_number>/', views_operations.delivery_confirm, name='delivery_confirm'),
    path('operations/update-status/', views_operations.update_status_lookup, name='update_status_lookup'),
    path('operations/update-status/<str:tracking_number>/', views_operations.update_status, name='update_status'),
    path('track/', views_operations.track_shipment, name='track_shipment'),
    path('track/<str:tracking_number>/', views_operations.track_result, name='track_result'),
    path('reports/', views_reports.reports_hub, name='reports_hub'),
    path('reports/<slug:slug>/', views_reports.report_view, name='report_view'),
    path('reports/<slug:slug>/export/<str:fmt>/', views_reports.report_export, name='report_export'),
]
