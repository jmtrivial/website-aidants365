from django.urls import path

from . import views

app_name = "fichier"

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('fiches/', views.index, name='index'),
    path('fiches/<int:id>/', views.index_detail, name='index_detail'),
    path('fiche/<int:id>/', views.detail, name='detail'),
    path('niveau/<int:id>/', views.index_niveau, name='index_niveau'),
    path('niveau/<int:id1>/<int:id2>/', views.index_niveau_detail, name='index_niveau_detail'),
    path('categorie/<int:id>/', views.index_categorie, name='index_categorie'),
    path('categorie/<int:id1>/<int:id2>/', views.index_categorie_detail, name='index_categorie_detail'),
    path('auteur/<int:id>/', views.index_auteur, name='index_auteur'),
    path('auteur/<int:id1>/<int:id2>/', views.index_auteur_detail, name='index_auteur_detail'),
    path('categorie_libre/<int:id>/', views.index_categorie_libre, name='index_categorie_libre'),
    path('categorie_libre/<int:id1>/<int:id2>/', views.index_categorie_libre_detail, name='index_categorie_libre_detail'),
    path('theme/<int:id>/', views.index_theme, name='index_theme'),
    path('theme/<int:id1>/<int:id2>/', views.index_theme_detail, name='index_theme_detail'),
    path('motcle/<int:id>/', views.index_motcle, name='index_motcle'),
    path('motcle/<int:id1>/<int:id2>/', views.index_motcle_detail, name='index_motcle_detail'),
]
