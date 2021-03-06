# Generated by Django 4.0.3 on 2022-03-15 15:08

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auteur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, verbose_name='Code auteur')),
                ('nom', models.CharField(max_length=64, verbose_name='Nom complet')),
                ('compte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Compte utilisateur correspondant')),
            ],
            options={
                'verbose_name': 'Auteur',
                'verbose_name_plural': 'Auteurs',
            },
        ),
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=4, unique=True, verbose_name='Code de la catégorie')),
                ('nom', models.CharField(max_length=64, verbose_name='Nom de la catégorie')),
                ('is_biblio', models.BooleanField(default=False, verbose_name='Nécessite les champs de bibliographie')),
                ('is_site', models.BooleanField(default=False, verbose_name='Nécessite les champs de site internet')),
            ],
            options={
                'verbose_name': 'Catégorie',
                'verbose_name_plural': 'Catégories',
            },
        ),
        migrations.CreateModel(
            name='CategorieLibre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=64, verbose_name='Nom de la catégorie libre')),
            ],
            options={
                'verbose_name': 'Catégorie libre',
                'verbose_name_plural': 'Catégories libres',
            },
        ),
        migrations.CreateModel(
            name='MotCle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=64, verbose_name='Mot-clé')),
            ],
            options={
                'verbose_name': 'Mot-clé',
                'verbose_name_plural': 'Mot-clés',
            },
        ),
        migrations.CreateModel(
            name='Niveau',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordre', models.IntegerField(unique=True, verbose_name='Numéro')),
                ('code', models.CharField(max_length=4, unique=True, verbose_name='Code')),
                ('nom', models.CharField(max_length=64, verbose_name='Nom')),
                ('description', models.CharField(blank=True, max_length=256, null=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Niveau',
                'verbose_name_plural': 'Niveaux',
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=64, verbose_name='Thème')),
            ],
            options={
                'verbose_name': 'Thème',
                'verbose_name_plural': 'Thèmes',
            },
        ),
        migrations.CreateModel(
            name='TypeCategorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=64, unique=True, verbose_name='Nom du type de catégorie')),
            ],
            options={
                'verbose_name': 'Type de catégorie',
                'verbose_name_plural': 'Types de catégorie',
            },
        ),
        migrations.CreateModel(
            name='Fiche',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(default=9999, verbose_name='Numéro')),
                ('titre_fiche', models.CharField(max_length=256, verbose_name='Titre de la fiche')),
                ('sous_titre', models.CharField(blank=True, max_length=256, verbose_name='Sous-titre')),
                ('date_creation', models.DateField(default=django.utils.timezone.now, verbose_name='Date de création')),
                ('date_derniere_modification', models.DateField(default=django.utils.timezone.now, verbose_name='Dernière modification')),
                ('url', models.URLField(blank=True, max_length=1024, verbose_name='Adresse')),
                ('titre', models.CharField(blank=True, max_length=1024, verbose_name="Titre de l'ouvrage")),
                ('auteurs', models.CharField(blank=True, max_length=1024, verbose_name='Auteurs')),
                ('date_publication', models.DateField(blank=True, null=True, verbose_name='Date de publication')),
                ('editeur', models.CharField(blank=True, max_length=1024, verbose_name='Éditeur')),
                ('format_bibl', models.CharField(blank=True, max_length=1024, verbose_name='Format')),
                ('partenaires', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Partenaires')),
                ('presentation', ckeditor.fields.RichTextField(blank=True, verbose_name='Présentation')),
                ('problematique', ckeditor.fields.RichTextField(blank=True, verbose_name='Problématique')),
                ('plan_du_site', ckeditor.fields.RichTextField(blank=True, verbose_name='Plan du site')),
                ('detail_focus', models.CharField(blank=True, max_length=1024, verbose_name='Détail du focus (placé après le mot "Focus")')),
                ('focus', ckeditor.fields.RichTextField(blank=True, verbose_name='Focus')),
                ('reserves', ckeditor.fields.RichTextField(blank=True, verbose_name='Réserves')),
                ('lesplus', ckeditor.fields.RichTextField(blank=True, verbose_name='Les plus')),
                ('en_savoir_plus', ckeditor.fields.RichTextField(blank=True, verbose_name='En savoir plus')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='fichier.auteur', verbose_name='Auteur')),
                ('categorie1', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='%(class)s_categorie1', to='fichier.categorie', verbose_name='Catégorie principale')),
                ('categorie2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_categorie2', to='fichier.categorie', verbose_name='Catégorie secondaire')),
                ('categorie3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_categorie3', to='fichier.categorie', verbose_name='Catégorie 3')),
                ('categories_libres', models.ManyToManyField(blank=True, to='fichier.categorielibre', verbose_name='Catégories libres')),
                ('fiches_connexes', models.ManyToManyField(blank=True, to='fichier.fiche', verbose_name='Fiches connexes')),
                ('mots_cles', models.ManyToManyField(blank=True, to='fichier.motcle', verbose_name='Mots-clés')),
                ('niveau', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='fichier.niveau', verbose_name='Niveau')),
                ('themes', models.ManyToManyField(blank=True, to='fichier.theme', verbose_name='Thèmes')),
            ],
            options={
                'verbose_name': 'Fiche',
                'verbose_name_plural': 'Fiches',
                'ordering': ['auteur', 'numero'],
            },
        ),
        migrations.AddField(
            model_name='categorie',
            name='type_categorie',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fichier.typecategorie', verbose_name='Type de la catégorie'),
        ),
    ]
