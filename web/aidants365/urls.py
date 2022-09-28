"""aidants365 URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', lambda req: redirect('fichier/')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('fichier/', include('fichier.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', auth_views.LoginView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = "fichier.views.page_not_found_view"
