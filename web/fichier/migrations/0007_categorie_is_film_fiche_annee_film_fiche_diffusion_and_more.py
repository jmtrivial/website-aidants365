# Generated by Django 4.0.3 on 2022-03-16 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0006_fiche_collection_fiche_quatrieme_de_couverture_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorie',
            name='is_film',
            field=models.BooleanField(default=False, verbose_name="Nécessite les champs d'un film"),
        ),
        migrations.AddField(
            model_name='fiche',
            name='annee_film',
            field=models.IntegerField(blank=True, default=2022, null=True, verbose_name='Année de production'),
        ),
        migrations.AddField(
            model_name='fiche',
            name='diffusion',
            field=models.IntegerField(blank=True, null=True, verbose_name='Diffusion'),
        ),
        migrations.AddField(
            model_name='fiche',
            name='duree',
            field=models.CharField(blank=True, max_length=32, verbose_name='Réalisateur(s)'),
        ),
        migrations.AddField(
            model_name='fiche',
            name='production',
            field=models.CharField(blank=True, max_length=1024, verbose_name='Production'),
        ),
        migrations.AddField(
            model_name='fiche',
            name='realisateurs',
            field=models.CharField(blank=True, max_length=1024, verbose_name='Réalisateur(s)'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='auteurs',
            field=models.CharField(blank=True, max_length=1024, verbose_name='Auteur(s)'),
        ),
    ]