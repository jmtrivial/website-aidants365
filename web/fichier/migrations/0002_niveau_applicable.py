# Generated by Django 4.0.3 on 2022-03-15 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='niveau',
            name='applicable',
            field=models.CharField(choices=[('A', 'Non applicable'), ('B', 'Moyennement applicable'), ('C', 'Immédiatement applicable')], default='B', max_length=1),
        ),
    ]
