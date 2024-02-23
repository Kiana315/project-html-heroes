# Generated by Django 5.0.2 on 2024-02-23 09:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("SocialDistribution", "0013_alter_comment_options_alter_like_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Follower",
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
                ("date_followed", models.DateTimeField(auto_now_add=True)),
                (
                    "follower",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reverse_followers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="followers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date_followed"],
                "unique_together": {("user", "follower")},
            },
        ),
        migrations.CreateModel(
            name="Following",
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
                ("date_followed", models.DateTimeField(auto_now_add=True)),
                (
                    "following",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reverse_following",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="following",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date_followed"],
                "unique_together": {("user", "following")},
            },
        ),
        migrations.DeleteModel(
            name="Follow",
        ),
    ]
