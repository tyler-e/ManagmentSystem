# Generated by Django 5.1.4 on 2025-01-17 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_spaceuser_user_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keyholder',
            name='is_prefered_keyholder',
        ),
        migrations.AddField(
            model_name='keyholder',
            name='priority',
            field=models.IntegerField(default=0),
        ),
    ]
