# Generated by Django 3.0.8 on 2020-12-23 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0024_auto_20201223_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(related_name='tag', to='recipes.Tag', verbose_name='Тег'),
        ),
    ]
