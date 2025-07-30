from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from newsletter.forms import RecipientForm, MailingListForm
from newsletter.models import Recipient, MailingList, SendAttempt, Message
from newsletter.services import Statistic


@method_decorator(cache_page(60*5), name='dispatch')
class HomeView(ListView):
    model = MailingList
    template_name = "newsletter/home_page.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        active_mailing_lists = MailingList.objects.filter(status=MailingList.STARTED)
        mailing_lists = MailingList.objects.all()
        unique_recipients = Recipient.objects.all()
        context = {"mailing_list": mailing_lists.count(),"active_mailing_list": active_mailing_lists.count(),"unique_recipient": unique_recipients.count()}
        return context


@method_decorator(cache_page(60*5), name='dispatch')
class RecipientListView(ListView):
    model = Recipient
    template_name = "newsletter/recipient_list.html"
    context_object_name = "recipient_list"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)


@method_decorator(cache_page(60*5), name='dispatch')
class RecipientDetailView(DetailView):
    model = Recipient
    template_name = "newsletter/recipient_detail.html"
    context_object_name = "recipient_detail"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not (request.user.is_staff or obj.owner == request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "newsletter/recipient_form.html"
    success_url = reverse_lazy("newsletter:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'newsletter/recipient_delete.html'
    success_url = reverse_lazy('newsletter:recipient_list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Получатель успешно удален')
        return super().delete(request, *args, **kwargs)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    fields = ['full_name', 'email', 'comment']
    template_name = 'newsletter/recipient_form.html'
    success_url = reverse_lazy('newsletter:recipient_list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)


@method_decorator(cache_page(60*5), name='dispatch')
class MailingListView(ListView):
    model = MailingList
    template_name = "newsletter/mailing_list.html"
    context_object_name = "mailing_list"

    def get_queryset(self):
        if self.request.user.is_staff:
            return MailingList.objects.all()
        return MailingList.objects.filter(owner=self.request.user)


@method_decorator(cache_page(60*5), name='dispatch')
class MailingDetailView(DetailView):
    model = MailingList
    template_name = "newsletter/mailing_detail.html"
    context_object_name = "mailing_detail"

    def get_context_data(self, *, object_list=None, **kwargs):
        mailing_list = MailingList.objects.get(pk=self.object.pk)
        recipients = mailing_list.recipients.all()
        context = {"mailing_list": mailing_list, "recipient_list": recipients}
        return context

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_staff and obj.owner != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MailingListCreateView(LoginRequiredMixin, CreateView):
    model = MailingList
    form_class =MailingListForm
    template_name = "newsletter/mailing_form.html"
    success_url = reverse_lazy("newsletter:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=self.request.user)
        return form


class MailingListUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingList
    form_class = MailingListForm
    template_name = 'newsletter/mailing_edit.html'
    success_url = reverse_lazy('newsletter:mailing_list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return MailingList.objects.all()
        return MailingList.objects.filter(owner=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            form.fields['message'].queryset = Message.objects.filter(owner=self.request.user)
            form.fields['recipients'].queryset = Recipient.objects.filter(owner=self.request.user)
        return form


class MailingListToggleView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        mailing = get_object_or_404(MailingList, pk=kwargs['pk'])
        if not (request.user.is_staff or mailing.owner.id == request.user.id):
            raise PermissionDenied("Вы не можете управлять этой рассылкой")
        mailing.is_active = not mailing.is_active
        mailing.save()
        if mailing.is_active and mailing.status == MailingList.CREATED:
            mailing.status = MailingList.STARTED
            mailing.save()
        messages.success(request, f'Рассылка {"включена" if mailing.is_active else "отключена"}')
        return redirect('newsletter:mailing_list')


class MailingListDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingList
    template_name = 'newsletter/mailing_confirm_delete.html'
    success_url = reverse_lazy('newsletter:mailing_list')

    def get_queryset(self):
        if self.request.user.is_staff:
            return MailingList.objects.all()
        return MailingList.objects.filter(owner=self.request.user)


class MailSend(View):
    success_url = reverse_lazy("newsletter:home_page")

    def post(self, *args, **kwargs):
        mailing_list = get_object_or_404(MailingList, id=self.kwargs["pk"])
        if not self.request.user.is_staff and mailing_list.owner != self.request.user:
            raise PermissionDenied
        mailing_list.send()
        return redirect(self.success_url)


class StatisticView(LoginRequiredMixin, TemplateView):
    template_name = 'newsletter/statistic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = Statistic.get_statistic(self.request.user)
        context.update(stats)
        return context


@method_decorator(cache_page(60*5), name='dispatch')
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'newsletter/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['title', 'body']
    template_name = 'newsletter/message_form.html'
    success_url = reverse_lazy('newsletter:mailing_create')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ['title', 'body']
    template_name = 'newsletter/message_form.html'
    success_url = reverse_lazy('newsletter:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'newsletter/message_delete.html'
    success_url = reverse_lazy('newsletter:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)
