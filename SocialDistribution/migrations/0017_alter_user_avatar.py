# Generated by Django 5.0.1 on 2024-02-25 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialDistribution', '0016_post_shared_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='avatars/default_avatar.png', upload_to='avatars/'),
        ),
    ]
