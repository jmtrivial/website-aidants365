from django.urls import path

from . import views

app_name = "fichier"

urlpatterns = [
    path('', views.index, name='index'),
    path('fiches/', views.index_fiches, name='index_fiches'),
    path('fiches/<int:id>/', views.detail, name='detail'),
]
