# Generated by Django 4.0.3 on 2022-11-13 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0039_entreeagenda_illustration_alt_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='entreeagenda',
            name='illustration_source',
            field=models.CharField(default='', max_length=512, verbose_name="Source de l'illustration."),
        ),
    ]
