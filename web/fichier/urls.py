from django.urls import path

from . import views


app_name = "fichier"

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('rechercher/', views.rechercher, name='rechercher'),
    path('fiches/', views.index, name='index'),
    path('fiches/<int:id>/', views.index_detail, name='index_detail'),
    path('fiche/<int:id>/', views.detail, name='detail'),
    path('fiche/<pk>/pdf/', views.FicheViewPDF.as_view(), name='detail_pdf'),
    path('niveau/<int:id>/', views.index_niveau, name='index_niveau'),
    path('niveau/<int:id1>/<int:id2>/', views.index_niveau_detail, name='index_niveau_detail'),
    path('categories/', views.categories, name='categories'),
    path('categories/alpha/', views.categories_alpha, name='categories_alpha'),
    path('categories/nuage/', views.categories_nuage, name='categories_nuage'),
    path('categorie/<int:id>/', views.index_categorie, name='index_categorie'),
    path('categorie/<pk>/delete/', views.DeleteCategorieView.as_view(), name='categorie_delete'),
    path('categorie/<int:id1>/<int:id2>/', views.index_categorie_detail, name='index_categorie_detail'),
    path('auteur/<int:id>/', views.index_auteur, name='index_auteur'),
    path('auteur/<int:id1>/<int:id2>/', views.index_auteur_detail, name='index_auteur_detail'),
    path('categorie_libre/<int:id>/', views.index_categorie_libre, name='index_categorie_libre'),
    path('categorie_libre/<int:id1>/<int:id2>/', views.index_categorie_libre_detail, name='index_categorie_libre_detail'),
    path('themes/', views.themes, name='themes'),
    path('themes/alpha/', views.themes_alpha, name='themes_alpha'),
    path('themes/nuage/', views.themes_nuage, name='themes_nuage'),
    path('theme/<int:id>/', views.index_theme, name='index_theme'),
    path('theme/<int:id1>/<int:id2>/', views.index_theme_detail, name='index_theme_detail'),
    path('motscles/', views.motscles, name='motscles'),
    path('motscles/alpha/', views.motscles_alpha, name='motscles_alpha'),
    path('motscles/nuage/', views.motscles_nuage, name='motscles_nuage'),
    path('motcle/<int:id>/', views.index_motcle, name='index_motcle'),
    path('motcle/<int:id1>/<int:id2>/', views.index_motcle_detail, name='index_motcle_detail'),
    path('glossaire/', views.glossaire, name='glossaire'),
    path('glossaire/<int:id>/', views.entree_glossaire, name='entree_glossaire'),
    path('glossaire/<pk>/delete/', views.DeleteEntreeGlossaireView.as_view(), name='entree_glossaire_delete'),
    path('agenda/', views.agenda, name='agenda'),
    path('agenda/<int:id>/', views.entree_agenda, name='entree_agenda'),
    path('agenda/<pk>/delete/', views.DeleteEntreeAgendaView.as_view(), name='entree_agenda_delete'),
    path('404/', views.page_not_found_view, name="page_not_found"),
    # pour ajouter et modifier des objets complexes, on utilise un formulaire
    path('<str:classname>/add/', views.edit_object, name='object_add'),
    path('<str:classname>/<int:id>/change/', views.edit_object, name='object_change'),
    # pour ajouter des objets simples, on utilise une API (uniquement POST implémenté)
    path('<str:classname>/api/', views.rest_api, name='rest_api')
]
