"""aidants365 URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect



urlpatterns = [
    path('', lambda req: redirect('fichier/')),
    path('fichier/', include('fichier.urls')),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
