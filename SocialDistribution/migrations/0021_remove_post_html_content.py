# Generated by Django 5.0.2 on 2024-03-04 06:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SocialDistribution', '0020_post_html_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='html_content',
        ),
    ]
