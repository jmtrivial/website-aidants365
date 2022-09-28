from django.urls import path

from . import views


app_name = "fichier"

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('rechercher/', views.rechercher, name='rechercher'),
    path('desk/', views.desk, name='desk'),
    path('desk/<int:id>/', views.document, name='document'),
    path('desk/<pk>/delete/', views.DeleteDocumentView.as_view(), name='document_delete'),
    path('fiches/', views.index, name='index'),
    path('fiches/<int:id>/', views.index_detail, name='index_detail'),
    path('fiche/<int:id>/', views.detail, name='detail'),
    path('fiche/<pk>/pdf/', views.FicheViewPDF.as_view(), name='detail_pdf'),
    path('fiche/<pk>/delete/', views.DeleteFicheView.as_view(), name='fiche_delete'),
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
    path('categorie_libre/<pk>/delete/', views.DeleteCategorieLibreView.as_view(), name='categorie_libre_delete'),
    path('themes/', views.themes, name='themes'),
    path('themes/alpha/', views.themes_alpha, name='themes_alpha'),
    path('themes/nuage/', views.themes_nuage, name='themes_nuage'),
    path('theme/<int:id>/', views.index_theme, name='index_theme'),
    path('theme/<int:id1>/<int:id2>/', views.index_theme_detail, name='index_theme_detail'),
    path('theme/<pk>/delete/', views.DeleteThemeView.as_view(), name='theme_delete'),
    path('motscles/', views.motscles, name='motscles'),
    path('motscles/alpha/', views.motscles_alpha, name='motscles_alpha'),
    path('motscles/nuage/', views.motscles_nuage, name='motscles_nuage'),
    path('motcle/<int:id>/', views.index_motcle, name='index_motcle'),
    path('motcle/<int:id1>/<int:id2>/', views.index_motcle_detail, name='index_motcle_detail'),
    path('motcle/<pk>/delete/', views.DeleteMotCleView.as_view(), name='motcle_delete'),
    path('glossaire/', views.glossaire, name='glossaire'),
    path('glossaire/<int:id>/', views.entree_glossaire, name='entree_glossaire'),
    path('glossaire/<pk>/delete/', views.DeleteEntreeGlossaireView.as_view(), name='entree_glossaire_delete'),
    path('agenda/', views.agenda_current_month, name='agenda'),
    path('agenda/<int:year>/', views.agenda_year, name='agenda_year'),
    path('agenda/<int:year>/<int:month>/', views.agenda_month, name='agenda_month'),
    path('agenda/<int:year>/<int:month>/<int:day>/', views.entree_agenda, name='entree_agenda'),
    path('agenda/entree/<int:id>/', views.entree_agenda_pk, name='entree_agenda_pk'),
    path('agenda/entree/<pk>/delete/', views.DeleteEntreeAgendaView.as_view(), name='entree_agenda_delete'),
    path('404/', views.page_not_found_view, name="page_not_found"),
    # pour ajouter et modifier les objets, on utilise un formulaire
    path('<str:classname>/add/', views.edit_object, name='object_add'),
    path('<str:classname>/<int:id>/change/', views.edit_object, name='object_change'),
    # pour ajouter des objets simples, on utilise une API (uniquement POST implémenté)
    path('<str:classname>/api/', views.rest_api, name='rest_api'),
    # pour les catégories simples, on propose la fusion
    path('<str:classname>/merge/', views.merge, name='merge')
]
