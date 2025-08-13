from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        Group.objects.all().delete()
        manager = Group.objects.create(name="Manager")

        view_mailing_list_permission = Permission.objects.get(codename="can_view_mailing_list")
        view_recipient_permission = Permission.objects.get(codename="can_view_recipient")
        view_user_list_permission = Permission.objects.get(codename="can_view_user_list")
        view_message_permission = Permission.objects.get(codename="can_view_message")
        view_attempts_permission = Permission.objects.get(codename="can_view_attempts")
        ban_permission = Permission.objects.get(codename="can_ban")
        turn_off_permission = Permission.objects.get(codename="can_turn_off")

        manager.permissions.add(
            view_mailing_list_permission,
            view_recipient_permission,
            view_user_list_permission,
            view_message_permission,
            view_attempts_permission,
            ban_permission,
            turn_off_permission,
        )
        manager.save()

        pm = User.objects.get(email="manager@man.com")
        pm.groups.add(manager)
