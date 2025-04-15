from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from accounts.views import signup_view
from . import views
from .views import custom_login_view
from .views import edit_coordinator_profile

from .views import (
    dashboard, home_redirect, CustomPasswordResetView,
    export_pdf, state_county_directory_view,
    community_post_create_view, community_post_list_view,
    edit_user_profile, update_referral, update_referral_status,
)

urlpatterns = [
    path('', home_redirect, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('signup/', signup_view, name='signup'),
    path('login/', custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('edit_profile/', views.edit_user_profile, name='edit_profile'),
    path('update-referral/', views.update_referral, name='update_referral'),
    path('update_referral_status/', views.update_referral_status, name='update_referral_status'),
    path('community/posts/create/', community_post_create_view, name='community_post_create'),
    path('community/posts/', community_post_list_view, name='community_post_list'),
    path('community/posts/export_pdf/', views.export_community_posts_pdf, name='export_community_posts_pdf'),
    path('community/post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('community/post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('community/posts/react/', views.toggle_reaction, name='toggle_reaction'),
    path('edit-coordinator/', views.edit_coordinator_profile, name='edit_coordinator_profile'),

    # State and County entities
    path('state-county-directory/export/pdf/', export_pdf, name='export_pdf'),
    path('state-county-directory/', state_county_directory_view, name='state_county_directory'),

    # Password Reset Routes
    path('password-reset/', CustomPasswordResetView.as_view(
        template_name='registration/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    path('accounts/', include('accounts.urls')),
]

# Only serve static/media files from Django during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
