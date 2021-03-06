# Generated by Django 4.0.3 on 2022-04-10 19:54

from django.db import migrations
import sortedm2m.fields
from sortedm2m.operations import AlterSortedManyToManyField


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0017_alter_entreeagenda_notes_alter_fiche_en_savoir_plus_and_more'),
    ]

    operations = [
        AlterSortedManyToManyField(
            model_name='entreeagenda',
            name='fiches_associees',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='fichier.fiche', verbose_name='Fiches associées'),
        ),
        AlterSortedManyToManyField(
            model_name='entreeagenda',
            name='motscles',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='fichier.motcle', verbose_name='Mots-clés associés'),
        ),
        AlterSortedManyToManyField(
            model_name='entreeagenda',
            name='themes',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='fichier.theme', verbose_name='Thèmes associés'),
        ),
        AlterSortedManyToManyField(
            model_name='fiche',
            name='categories_libres',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='fichier.categorielibre', verbose_name='Catégories libres'),
        ),
        AlterSortedManyToManyField(
            model_name='fiche',
            name='fiches_connexes',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='fichier.fiche', verbose_name='Fiches connexes'),
        ),
        AlterSortedManyToManyField(
            model_name='fiche',
            name='mots_cles',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='fichier.motcle', verbose_name='Mots-clés'),
        ),
        AlterSortedManyToManyField(
            model_name='fiche',
            name='themes',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='fichier.theme', verbose_name='Thèmes'),
        ),
    ]
