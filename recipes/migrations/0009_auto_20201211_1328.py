# Generated by Django 3.0.8 on 2020-12-11 10:28

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_remove_tag_checkbox_style'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.Ingredient'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tag',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='tag', to='recipes.Tag'),
            preserve_default=False,
        ),
    ]
