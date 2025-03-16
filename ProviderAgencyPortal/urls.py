from django.contrib import admin
from django.urls import path, include  # Import necessary functions
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin Panel
    path('', include('myapp.urls')),  # Includes all routes from `myapp.urls`

    # Password reset URLs
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),  # Request password reset
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # Password reset sent
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # Password reset confirmation
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Password reset complete
]
