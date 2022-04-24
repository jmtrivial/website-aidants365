# Generated by Django 4.0.3 on 2022-04-24 08:01

import ckeditor.fields
from django.db import migrations, models
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0021_auto_20220424_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='entreeagenda',
            name='marque',
            field=models.BooleanField(default=False, verbose_name='Entrée de qualité'),
        ),
        migrations.AddField(
            model_name='fiche',
            name='marque',
            field=models.BooleanField(default=False, verbose_name='Entrée de qualité'),
        ),
        migrations.AlterField(
            model_name='entreeagenda',
            name='fiches_associees',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text="L'ordre des éléments peut être changé glisser/déposer", to='fichier.fiche', verbose_name='Fiches associées'),
        ),
        migrations.AlterField(
            model_name='entreeagenda',
            name='motscles',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text="L'ordre des éléments peut être changé glisser/déposer", to='fichier.motcle', verbose_name='Mots-clés associés'),
        ),
        migrations.AlterField(
            model_name='entreeagenda',
            name='notes',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='entreeagenda',
            name='themes',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text="L'ordre des éléments peut être changé glisser/déposer", to='fichier.theme', verbose_name='Thèmes associés'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='categories_libres',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text="L'ordre des éléments peut être changé glisser/déposer", to='fichier.categorielibre', verbose_name='Catégories libres'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='en_savoir_plus',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='En savoir plus'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='fiches_connexes',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text="L'ordre des éléments peut être changé glisser/déposer", to='fichier.fiche', verbose_name='Fiches connexes'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='focus',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='Focus'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='lesplus',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='Les plus'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='mots_cles',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text="L'ordre des éléments peut être changé glisser/déposer", to='fichier.motcle', verbose_name='Mots-clés'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='plan_du_site',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='Plan du site'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='presentation',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='Présentation'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='problematique',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='Problématique'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='quatrieme_de_couverture',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='Quatrième de couverture'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='reserves',
            field=ckeditor.fields.RichTextField(blank=True, help_text="Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant]).", verbose_name='Réserves'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='themes',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text="L'ordre des éléments peut être changé glisser/déposer", to='fichier.theme', verbose_name='Thèmes'),
        ),
    ]
