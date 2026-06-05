from django.urls import path

from . import views
from . import views_management

app_name = 'account'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('users/', views_management.user_list, name='user_list'),
    path('users/add/', views_management.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views_management.user_edit, name='user_edit'),
    path('users/<int:pk>/toggle-status/', views_management.user_toggle_status, name='user_toggle_status'),
]
