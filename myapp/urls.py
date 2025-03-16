from django.urls import path
from django.contrib.auth import views as auth_views  # Add this import to handle password reset views
from .views import login_view, logout_view, signup_view, dashboard_view, agency_details, terms  # Ensure terms_of_service is imported
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('login/', login_view, name='login'),      # Login Page
    path('logout/', logout_view, name='logout'),  # Logout Page
    path('signup/', signup_view, name='signup'),  # Sign-Up Page
    path('dashboard/', dashboard_view, name='dashboard'),  # Dashboard Page
    path('dashboard/agency/<int:agency_id>/', agency_details, name='agency_details'),  # Added API Route for agency details

    # Password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),  # Request password reset
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),  # Password reset sent
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # Password reset confirmation
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),  # Password reset complete

    # Terms of Service page route
    path('terms_of_service/', terms, name='terms_of_service'),  # Terms of Service Page
]
