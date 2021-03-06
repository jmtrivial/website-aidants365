# Generated by Django 4.0.3 on 2022-03-16 17:31

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0005_remove_fiche_date_publication_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fiche',
            name='collection',
            field=models.CharField(blank=True, max_length=1024, verbose_name='Collection'),
        ),
        migrations.AddField(
            model_name='fiche',
            name='quatrieme_de_couverture',
            field=ckeditor.fields.RichTextField(blank=True, verbose_name='Quatrième de couverture'),
        ),
        migrations.AlterField(
            model_name='fiche',
            name='date_derniere_modification',
            field=models.DateTimeField(auto_now=True, verbose_name='Dernière modification'),
        ),
    ]
