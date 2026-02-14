"""
URL configuration for housemd_escape_room_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from housemd_escape_room import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Existing URLs
    path('', views.home, name='home'),
    path('booking/', views.booking, name='booking'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='housemd_escape_room/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking-confirmation/<str:order_number>/', views.booking_confirmation, name='booking_confirmation'),
    
    # Password Reset URLs
    path('password-reset/', 
     auth_views.PasswordResetView.as_view(
         template_name='housemd_escape_room/password_reset.html',
         email_template_name='registration/password_reset_email.txt',  # Plain text fallback
         html_email_template_name='registration/password_reset_email.html',  # YOUR HTML TEMPLATE
         subject_template_name='registration/password_reset_subject.txt',  # Optional: custom subject
     ), 
     name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='housemd_escape_room/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='housemd_escape_room/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='housemd_escape_room/password_reset_complete.html'), name='password_reset_complete'),
    
    # NEW CRUD URLs
    path('booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('booking/<int:pk>/edit/', views.edit_booking, name='edit_booking'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
]