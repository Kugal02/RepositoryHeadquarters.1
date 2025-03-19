from django.urls import path
from django.contrib.auth import views as auth_views
from .views import login_view, logout_view, signup_view, dashboard_view, agency_details, terms

urlpatterns = [
    path('login/', login_view, name='login'),      # Login Page
    path('logout/', logout_view, name='logout'),  # Logout Page
    path('signup/', signup_view, name='signup'),  # Sign-Up Page
    path('dashboard/', dashboard_view, name='dashboard'),  # Dashboard Page

    # API Route for agency details (this is the API endpoint your JS is calling)
    path('api/agency/<int:agency_id>/', agency_details, name='get_agency_details'),  # API route for agency details
    path('api/agency/<int:agency_id>/', agency_details, name='agency_details'),

    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Terms of Service page route
    path('terms_of_service/', terms, name='terms_of_service'),  # Terms of Service Page
]
