# Generated by Django 3.0.8 on 2020-12-23 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0026_auto_20201223_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cook_time',
            field=models.PositiveIntegerField(default=2, verbose_name='Время приготовления'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ForeignKey(default=4509, on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.Ingredient', verbose_name='Ингредиенты'),
            preserve_default=False,
        ),
    ]
