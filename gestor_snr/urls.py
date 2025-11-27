"""
URL configuration for gestor_snr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- RUTAS DE RESTABLECIMIENTO DE CONTRASEÑA (PERSONALIZADAS) ---
    # Es vital definirlas ANTES del include para que ganen prioridad
    
    path('accounts/password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/recuperar_form.html'), 
         name='password_reset'),

    path('accounts/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/recuperar_enviado.html'), 
         name='password_reset_done'),

    path('accounts/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/recuperar_confirmar.html'), 
         name='password_reset_confirm'),

    path('accounts/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/recuperar_exito.html'), 
         name='password_reset_complete'),

    # ---------------------------------------------------------------
    
    # Incluimos las URLs de autenticación de Django (Login/Logout)
    # Esto es necesario para que {% url 'logout' %} funcione en el menú
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('notificaciones.urls')),
]
