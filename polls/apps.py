from django.apps import AppConfig
from django.contrib.auth import get_user_model
import os

class PollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'

    def ready(self):
        User = get_user_model()

        admin_user = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        admin_email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        admin_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        # Only create if credentials exist and user doesn't already exist
        if admin_user and admin_password:
            if not User.objects.filter(username=admin_user).exists():
                print("✅ Creating Django superuser...")
                User.objects.create_superuser(
                    username=admin_user,
                    email=admin_email,
                    password=admin_password
                )
                print("✅ Superuser created!")
