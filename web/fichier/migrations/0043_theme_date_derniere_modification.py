# Generated by Django 4.0.3 on 2022-12-09 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0042_categorie_date_derniere_modification_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='date_derniere_modification',
            field=models.DateTimeField(auto_now=True, verbose_name='Dernière modification'),
        ),
    ]
