# Generated by Django 4.0.3 on 2022-03-15 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichier', '0002_niveau_applicable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='niveau',
            name='applicable',
            field=models.CharField(choices=[('A', 'Théorique'), ('B', 'Intermédiaire'), ('C', 'Pratique')], default='B', max_length=1),
        ),
    ]
