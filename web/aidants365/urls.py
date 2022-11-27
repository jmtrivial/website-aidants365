"""aidants365 URL Configuration
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.views.static import serve
from django.views.static import serve
from . import views


urlpatterns = [
    path('', lambda req: redirect('fichier/')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('fichier/', include('fichier.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', auth_views.LoginView.as_view()),
    path('media/fiches.pdf', views.protected_serve, {'document_url': settings.MEDIA_URL, 'document_root': settings.MEDIA_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = "fichier.views.page_not_found_view"
