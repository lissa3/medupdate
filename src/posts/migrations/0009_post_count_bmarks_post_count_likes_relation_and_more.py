# Generated by Django 4.2.1 on 2024-02-06 17:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("posts", "0008_alter_post_categ"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="count_bmarks",
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="post",
            name="count_likes",
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.CreateModel(
            name="Relation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("like", models.BooleanField(blank=True, null=True)),
                ("in_bookmark", models.BooleanField(blank=True, default=False)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post_rel",
                        to="posts.post",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_rel",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="post",
            name="fans",
            field=models.ManyToManyField(
                related_name="post_fans",
                through="posts.Relation",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="relation",
            constraint=models.UniqueConstraint(
                fields=("user", "post"), name="unique_rels"
            ),
        ),
    ]
