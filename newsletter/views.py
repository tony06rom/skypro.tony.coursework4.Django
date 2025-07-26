from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from newsletter.models import Recipient, MailingList


class HomeView(ListView):
    model = MailingList
    template_name = "newsletter/home_page.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        active_mailing_lists = MailingList.objects.filter(status="started")
        mailing_lists = MailingList.objects.all()
        unique_recipients = Recipient.objects.all()
        context = {"mailing_list": mailing_lists.count(),"active_mailing_list": active_mailing_lists.count(),"unique_recipient": unique_recipients.count()}
        return context


class SendMail(View):
    success_url = reverse_lazy("newsletter:mailing_list")

    def post(self, *args, **kwargs):
        mailing_list = get_object_or_404(MailingList, id=self.kwargs["pk"])
        mailing_list.send()
        return redirect(self.success_url)


class RecipientListView(ListView):
    model = Recipient
    template_name = "newsletter/recipient_list.html"
    context_object_name = "recipient_list"


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = "newsletter/recipient_detail.html"
    context_object_name = "recipient_detail"


class MailingListView(ListView):
    model = MailingList
    template_name = "newsletter/mailing_list.html"
    context_object_name = "mailing_list"


class MailingDetailView(DetailView):
    model = MailingList
    template_name = "newsletter/mailing_detail.html"
    context_object_name = "mailing_detail"

    def get_context_data(self, *, object_list=None, **kwargs):
        mailing_list = MailingList.objects.get(pk=self.object.pk)
        recipients = mailing_list.recipients.all()
        context = {"mailing_list": mailing_list, "recipient_list": recipients}
        return context


class MailSend(View):
    success_url = reverse_lazy("newsletter:home_page")

    def post(self, *args, **kwargs):
        mailing_list = get_object_or_404(MailingList, id=self.kwargs["pk"])
        mailing_list.send()
        return redirect(self.success_url)
