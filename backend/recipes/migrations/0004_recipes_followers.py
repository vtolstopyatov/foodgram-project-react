# Generated by Django 4.1.3 on 2023-04-15 21:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0003_remove_ingredientsamount_ingredients_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipes',
            name='followers',
            field=models.ManyToManyField(related_name='favorite', to=settings.AUTH_USER_MODEL),
        ),
    ]