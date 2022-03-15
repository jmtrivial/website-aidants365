from django.urls import path

from . import views

app_name = "fichier"

urlpatterns = [
    path('', views.index, name='index'),
    path('fiches/', views.index_fiches, name='index_fiches'),
    path('fiche/<int:id>/', views.detail, name='detail'),
    path('niveau/<int:id>/', views.index_niveau, name='index_niveau'),
    path('categorie/<int:id>/', views.index_categorie, name='index_categorie'),
    path('auteur/<int:id>/', views.index_auteur, name='index_auteur'),
    path('categorie_libre/<int:id>/', views.index_categorie_libre, name='index_categorie_libre'),
    path('theme/<int:id>/', views.index_theme, name='index_theme'),
    path('theme/<int:id>/<int:id>/', views.index_theme_detail, name='index_theme_detail'),
    path('motcle/<int:id>/', views.index_motcle, name='index_motcle'),
]
