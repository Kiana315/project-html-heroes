# Generated by Django 5.0.1 on 2024-02-11 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialDistribution', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='static/avatars/'),
        ),
    ]
