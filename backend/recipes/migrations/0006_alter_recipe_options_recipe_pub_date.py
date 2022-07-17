# Generated by Django 4.0.6 on 2022-07-17 17:06

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_favorite_recipe_alter_favorite_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AddField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2022, 7, 17, 17, 6, 58, 34015, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
