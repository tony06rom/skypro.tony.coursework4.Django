import os

from django.core.mail import send_mail
from django.db import models

from users.models import User


class Recipient(models.Model):
    email = models.EmailField(verbose_name="Email", unique=True, help_text="Введите e-mail")
    full_name = models.CharField(max_length=60, verbose_name="ФИО", help_text="Введите ФИО")
    comment = models.TextField(max_length=500, blank=True, verbose_name="Комментарий", help_text="Добавьте комментарий")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='Владелец', related_name='recipient_owner')

    def __str__(self):
        return f"{self.email} | {self.full_name}"

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["email"]


class Message(models.Model):
    title = models.CharField(max_length=100, verbose_name="Тема письма", help_text="Введите тему письма")
    body = models.TextField(max_length=500, verbose_name="Тело письма",  help_text="Напишите текст письма")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='Владелец', related_name='message_owner')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["title"]


class MailingList(models.Model):
    CREATED = 'created'
    STARTED = 'started'
    COMPLETED = 'completed'
    STATUS_CHOICES = [(CREATED, "Создана"),(STARTED, "Запущена"),(COMPLETED, "Завершена")]

    date_first_sent = models.DateTimeField(auto_now_add=True, verbose_name="Дата первой отправки")
    date_last_sent = models.DateTimeField(auto_now=True, verbose_name="Дата последней отправки", )
    status = models.CharField(choices=STATUS_CHOICES, default="created", verbose_name="Статус", help_text="Выберите статус")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение", help_text="Введите сообщение")
    recipients = models.ManyToManyField(Recipient, verbose_name="Получатели", help_text="Введите получателей")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='Владелец', related_name='mailing_owner')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    def __str__(self):
        return f"{self.pk} | {self.recipients} | {self.status}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["status"]

    def send(self):
        self.status = self.STARTED
        self.save()
        subject = self.message.title
        message = self.message.body
        from_email = os.getenv("EMAIL_HOST_USER")
        recipient_list = [r.email for r in self.recipients.all()]

        try:
            success_count = send_mail(subject, message, from_email, recipient_list, fail_silently=False,)
            self.status = self.COMPLETED
            self.save()
            SendAttempt.objects.create(mailing_list=self, status=SendAttempt.SUCCESS, response="Письма успешно отправлены", owner=self.owner)
            return success_count
        except Exception as e:
            SendAttempt.objects.create(mailing_list=self, status=SendAttempt.FAILURE, response=str(e), owner=self.owner)
            self.status = self.COMPLETED
            self.save()
            return 0


class SendAttempt(models.Model):
    SUCCESS = 'success'
    FAILURE = 'failure'
    STATUS_CHOICES = [(SUCCESS, "Успешно"), (FAILURE, "Не успешно")]

    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")
    status = models.CharField(choices=STATUS_CHOICES, verbose_name="Статус")
    response = models.TextField(blank=True, verbose_name="Ответ почтового сервера")
    mailing_list = models.ForeignKey(MailingList, on_delete=models.CASCADE, verbose_name="Рассылка")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='Владелец', related_name='attempt_owner')

    def __str__(self):
        return f"{self.date} | id:{self.mailing_list.pk} | {self.status} | {self.response}"

    class Meta:
        verbose_name = "Состояние рассылки"
        verbose_name_plural = "Состояния рассылок"
        ordering = ["status", "date"]
