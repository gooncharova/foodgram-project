# Generated by Django 3.0.8 on 2021-01-13 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0037_auto_20210113_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.Amount', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
    ]
