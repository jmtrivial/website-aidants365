# Generated by Django 4.0.3 on 2022-03-16 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0004_alter_niveau_applicable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fiche',
            name='date_publication',
        ),
        migrations.AddField(
            model_name='fiche',
            name='annee_publication',
            field=models.IntegerField(blank=True, default=2022, null=True, verbose_name='Année de publication'),
        ),
    ]
