# Generated by Django 5.1.4 on 2025-01-17 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visit_tracking', '0002_visit_forgot_to_signout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='exit_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
