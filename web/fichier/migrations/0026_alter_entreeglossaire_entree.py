# Generated by Django 4.0.3 on 2022-09-30 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0025_alter_fiche_format_bibl_alter_niveau_applicable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entreeglossaire',
            name='entree',
            field=models.CharField(max_length=128, verbose_name='Entrée'),
        ),
    ]