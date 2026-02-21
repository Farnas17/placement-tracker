from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import register_view

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),

    path(
        'login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path('register/', register_view, name='register'),
]