from django.urls import path

from . import views

app_name = 'main_app'

urlpatterns = [
    path('settings/branding/', views.branding_settings, name='branding_settings'),
]
