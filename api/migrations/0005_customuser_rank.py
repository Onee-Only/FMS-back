# Generated by Django 3.2 on 2022-10-19 05:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_game_weekday'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='rank',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
