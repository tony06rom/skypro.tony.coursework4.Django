from django.core.management import BaseCommand
from django.shortcuts import get_object_or_404

from newsletter.models import MailingList
from users.models import User


class Command(BaseCommand):
    help = "Create new users"

    def handle(self, *args, **options):
        email = input("Введите ваш email: ")
        recipient = get_object_or_404(User, email=email)
        mailing_lists = MailingList.objects.all()
        print("Список рассылок на отправку:")
        for mailing_list in mailing_lists.filter(status__in=[MailingList.CREATED, MailingList.STARTED]):
            print(mailing_list)
        pk = input("Выберите рассылку (id): ")
        mailing_list = get_object_or_404(MailingList, id=pk)
        if mailing_list:
            mailing_list.send()
        else:
            print("Рассылка не удалась")
