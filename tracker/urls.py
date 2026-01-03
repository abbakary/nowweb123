from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from . import views
from . import views_frontend

# Frontend URLs
frontend_patterns = [
    path('', views_frontend.home, name='home'),
    path('services/', views_frontend.services, name='services'),
    path('service/<int:pk>/', views_frontend.service_detail, name='service_detail'),
    path('contact/', views_frontend.contact, name='contact'),
    path('about/', views_frontend.about, name='about'),
    path('privacy/', views_frontend.privacy, name='privacy'),
    path('terms/', views_frontend.terms, name='terms'),
    
    # Service requests
    path('service/<int:pk>/request/', views_frontend.service_request, name='service_request'),
    
    # Workshop URLs
    path('workshop/<int:pk>/', views_frontend.workshop_detail, name='workshop_detail'),
    path('workshop/<int:pk>/register/', views_frontend.register_workshop, name='register_workshop'),
    
    # Client Dashboard
    path('dashboard/', views_frontend.client_dashboard, name='client_dashboard'),
]

# Authentication URLs
auth_patterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html'
    ), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
]

# User Profile URLs
profile_patterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/password-change/', views.change_password, name='change_password'),
    path('profile/settings/', views.user_settings, name='user_settings'),
]

# Admin URLs
admin_patterns = [
    path('admin/dashboard/', views_frontend.admin_dashboard, name='admin_dashboard'),
    path('admin/overview/', views_frontend.admin_overview, name='admin_overview'),
    path('admin/services/', views_frontend.admin_services, name='admin_services'),
    path('admin/consultancy/', views_frontend.admin_consultancy, name='admin_consultancy'),
    path('admin/clients/', views_frontend.admin_clients, name='admin_clients'),
    path('admin/requests/', views_frontend.admin_requests, name='admin_requests'),
    path('admin/workshops/', views_frontend.admin_workshops, name='admin_workshops'),
    path('admin/zoom-appointments/', views_frontend.admin_zoom_appointments, name='admin_zoom_appointments'),
    path('admin/testimonials/', views_frontend.admin_testimonials, name='admin_testimonials'),
    path('admin/reports/', views_frontend.admin_reports, name='admin_reports'),
]

# API URLs (JSON responses for AJAX)
api_patterns = [
    path('api/check-username/', views.check_username_availability, name='check_username_api'),
    path('api/check-email/', views.check_email_availability, name='check_email_api'),
    path('api/get-services/', views.get_services_json, name='get_services_api'),
    path('api/get-testimonials/', views.get_testimonials_json, name='get_testimonials_api'),
    path('api/get-workshops/', views.get_workshops_json, name='get_workshops_api'),
    path('api/submit-contact/', views.submit_contact_ajax, name='submit_contact_ajax'),
]

urlpatterns = frontend_patterns + auth_patterns + profile_patterns + admin_patterns + api_patterns
