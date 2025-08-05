from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        User.objects.all().delete()
        user, created = User.objects.get_or_create(
            email="admin@adm.com",
            defaults={
                'is_staff': True,
                'is_active': True,
                'is_superuser': True
            }
        )
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password("Qwerty12345!")
        user.save()
        self.stdout.write(self.style.SUCCESS('Пользователь admin создан'))

        user, created = User.objects.get_or_create(
            email="manager@man.com",
            defaults={
                'is_staff': True,
                'is_active': True,
            }
        )
        user.is_staff = True
        user.is_active = True
        user.set_password("Qwerty12345!")
        user.save()
        self.stdout.write(self.style.SUCCESS('Пользователь manager создан'))