from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup, dashboard, home_redirect, CustomPasswordResetView, state_county_entities, export_csv, export_pdf
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home_redirect, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('state-county-entities/', state_county_entities, name='state_county_entities'),
    path('state-county-entities/export/csv/', export_csv, name='export_csv'),
    path('state-county-entities/export/pdf/', export_pdf, name='export_pdf'),

    path('password-reset/', CustomPasswordResetView.as_view(
        template_name='registration/password_reset.html'), name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
