from django.urls import path
from .views import signup_view, CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
