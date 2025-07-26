from django.contrib import admin

from newsletter.models import Recipient, Message, MailingList, SendAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name",)
    list_filter = ("email", "full_name",)
    search_fields = ("email", "full_name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("title",)
    list_filter = ("title",)
    search_fields = ("title",)


@admin.register(MailingList)
class MailingListAdmin(admin.ModelAdmin):
    list_display = ("message", "status", "date_first_sent", "date_last_sent",)
    list_filter = ("status", "recipients", "date_first_sent", "date_last_sent",)
    search_fields = ("status", "recipients", "date_first_sent", "date_last_sent",)


@admin.register(SendAttempt)
class SendAttemptAdmin(admin.ModelAdmin):
    list_display = ("date", "status", "response", "mailing_list",)
    list_filter = ("date", "status", "mailing_list",)
    search_fields = ("date", "status", "mailing_list",)
