# Generated by Django 4.0.3 on 2022-03-16 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0007_categorie_is_film_fiche_annee_film_fiche_diffusion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fiche',
            name='diffusion',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Diffusion'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='duree',
            field=models.CharField(blank=True, max_length=32, verbose_name='Durée'),
        ),
    ]
