# Generated by Django 4.2.1 on 2024-02-01 09:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comments", "0003_comment_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="own_reply",
            field=models.BooleanField(default=False),
        ),
    ]
