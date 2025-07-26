from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        User.objects.get(email="admin@adm.com").delete()
        user = User.objects.create(email="admin@adm.com")
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password("qwerty12345")
        user.save()
