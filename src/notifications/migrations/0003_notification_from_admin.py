# Generated by Django 4.2.1 on 2024-02-20 13:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0002_notification_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="from_admin",
            field=models.BooleanField(default=False),
        ),
    ]
