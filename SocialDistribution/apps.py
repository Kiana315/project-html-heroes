from django.apps import AppConfig


class SocialdistributionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "SocialDistribution"

    def ready(self):
        from .models import SignUpSettings
        if not SignUpSettings.objects.exists():
            SignUpSettings.objects.create()
