from django.urls import path

from . import views
from . import views_management
from . import views_packages

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
]
