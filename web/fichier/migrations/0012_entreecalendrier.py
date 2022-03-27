# Generated by Django 4.0.3 on 2022-03-27 20:50

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0011_alter_entreeglossaire_entree_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntreeCalendrier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('notes', ckeditor.fields.RichTextField(blank=True, verbose_name='Notes')),
                ('fiches_associees', models.ManyToManyField(blank=True, to='fichier.fiche', verbose_name='Fiches associées')),
                ('motscles', models.ManyToManyField(blank=True, to='fichier.motcle', verbose_name='Mots-clés associées')),
                ('themes', models.ManyToManyField(blank=True, to='fichier.theme', verbose_name='Thèmes associées')),
            ],
            options={
                'verbose_name': 'Entrée du calendrier',
                'verbose_name_plural': 'Entrées du calendrier',
            },
        ),
    ]