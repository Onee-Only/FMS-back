# Generated by Django 3.2 on 2022-10-09 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20221006_2309'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='weekday',
            field=models.IntegerField(default=0),
        ),
    ]
