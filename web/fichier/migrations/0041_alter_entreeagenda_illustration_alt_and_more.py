# Generated by Django 4.0.3 on 2022-11-15 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0040_entreeagenda_illustration_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entreeagenda',
            name='illustration_alt',
            field=models.CharField(blank=True, default='', max_length=512, null=True, verbose_name="Texte alternatif à l'illustration (audiodescription)"),
        ),
        migrations.AlterField(
            model_name='entreeagenda',
            name='illustration_source',
            field=models.CharField(blank=True, default='', max_length=512, null=True, verbose_name="Source de l'illustration"),
        ),
    ]
