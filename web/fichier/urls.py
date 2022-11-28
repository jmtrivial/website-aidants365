from django.urls import path, re_path

from . import views

from django.views.decorators.cache import cache_page

app_name = "fichier"

# durée cache par défaut
dcp = 2 * 60   # 2 mn
dcf = 15 * 60  # 15 mn
oneday = 60 * 60 * 24

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
    path('themes/', views.themes, name='themes'),
    path('themes/alpha/', views.themes_alpha, name='themes_alpha'),
    path('themes/nuage/', views.themes_nuage, name='themes_nuage'),
    path('theme/<int:id>/', views.index_theme, name='index_theme'),
    path('theme/<int:id1>/<int:id2>/', views.index_theme_detail, name='index_theme_detail'),
    path('theme/<pk>/delete/', views.DeleteThemeView.as_view(), name='theme_delete'),
    path('etiquettes/', views.etiquettes, name='etiquettes'),
    path('etiquettes/page/<int:key>', views.etiquettes_page, name='etiquettes_page'),
    path('etiquettes/alpha/', views.etiquettes_alpha, name='etiquettes_alpha'),
    re_path(r'^etiquettes/alpha/(?P<key>[A-Z\-])/$', views.etiquettes_alpha_page, name='etiquettes_alpha_page'),
    path('etiquettes/nuage/', cache_page(dcf)(views.etiquettes_nuage), name='etiquettes_nuage'),
    path('etiquette/<int:id>/', views.index_etiquette, name='index_etiquette'),
    path('etiquette/<int:id1>/<int:id2>/', views.index_etiquette_detail, name='index_etiquette_detail'),
    path('etiquette/<pk>/delete/', views.DeleteEtiquetteView.as_view(), name='etiquette_delete'),
    path('glossaire/', views.glossaire, name='glossaire'),
    re_path(r'^glossaire/(?P<key>[A-Z\-])/$', views.glossaire_page, name='glossaire_page'),
    path('glossaire/<int:id>/', views.entree_glossaire, name='entree_glossaire'),
    path('glossaire/search/<str:txt>/', views.recherche_glossaire, name='recherche_glossaire'),
    path('glossaire/<pk>/delete/', views.DeleteEntreeGlossaireView.as_view(), name='entree_glossaire_delete'),
    path('agenda/', views.agenda_current_month, name='agenda'),
    path('agenda/<int:year>/', cache_page(dcf)(views.agenda_year), name='agenda_year'),
    path('agenda/<int:year>/<int:month>/', views.agenda_month, name='agenda_month'),
    path('agenda/<int:year>/<int:month>/details/', views.agenda_month_details, name='agenda_month_details'),
    path('agenda/<int:year>/<int:month>/<int:day>/', views.entree_agenda, name='entree_agenda'),
    path('agenda/entree/<int:id>/', views.entree_agenda_pk, name='entree_agenda_pk'),
    path('agenda/entree/<pk>/pdf/', views.EntreeAgendaViewPDF.as_view(), name='entree_agenda_pdf'),
    path('agenda/entree/<pk>/pdftest/', views.entree_agenda_pdf_test, name='entree_agenda_pdf_test'),
    path('agenda/entree/<pk>/delete/', views.DeleteEntreeAgendaView.as_view(), name='entree_agenda_delete'),
    path('agenda/entree/<pk>/inverser/', views.entree_agenda_invert_with, name='entree_agenda_invert_with'),
    path('agenda/inverser/', views.entree_agenda_invert, name='entree_agenda_invert'),
    path('agenda/sans-niveau/', views.agenda_sans_niveau, name='agenda_sans_niveau'),
    path('404/', views.page_not_found_view, name="page_not_found"),
    # pour ajouter et modifier les objets, on utilise un formulaire
    path('<str:classname>/add/', views.edit_object, name='object_add'),
    path('<str:classname>/<int:id>/change/', views.edit_object, name='object_change'),
    path('<str:classname>/<int:id>/duplicate/', views.duplicate_object, name='object_duplicate'),
    # pour ajouter des objets simples, on utilise une API (uniquement POST implémenté)
    path('<str:classname>/api/', views.rest_api, name='rest_api'),
    # pour les catégories simples, on propose la fusion
    path('<str:classname>/merge/', views.merge, name='merge'),
    path('modifications/', views.modifications, name='modifications'),
    path('modifications/page/<int:key>', views.modifications_page, name='modifications_page'),
    path('<str:classname>/modifications/', views.simple_modifications, name='simple_modifications'),
    path('<str:classname>/modifications/page/<int:key>', views.simple_modifications_page, name='simple_modifications_page'),
    path('liens-sortants/', views.liens_sortants, name='liens_sortants'),
    path('a-propos/', views.a_propos, name='a_propos'),
]
