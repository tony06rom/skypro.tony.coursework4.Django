from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from newsletter.forms import MailingListForm, RecipientForm
from newsletter.models import MailingList, Message, Recipient
from newsletter.services import Statistic
from django.core.cache import cache


class HomeView(ListView):
    model = MailingList
    template_name = "newsletter/home_page.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        active_mailing_lists = MailingList.objects.filter(status=MailingList.STARTED)
        mailing_lists = MailingList.objects.all()
        unique_recipients = Recipient.objects.all()
        context = {
            "mailing_list": mailing_lists.count(),
            "active_mailing_list": active_mailing_lists.count(),
            "unique_recipient": unique_recipients.count(),
        }
        return context


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "newsletter/recipient_list.html"
    context_object_name = "recipient_list"

    def get_queryset(self):
        cache_key = f'recipient:{self.request.user.pk}'
        queryset = cache.get(cache_key)
        if not queryset:
            if self.request.user.has_perm("newsletter.can_view_recipient"):
                queryset = Recipient.objects.all()
            else:
                queryset = Recipient.objects.filter(owner=self.request.user)
            cache.set(cache_key, queryset, 60 * 5)
        return queryset


class RecipientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Recipient
    template_name = "newsletter/recipient_detail.html"
    context_object_name = "recipient_detail"
    permission_required = "newsletter.can_view_recipient"

    def has_permission(self):
        instance = self.get_object()
        if instance.owner == self.request.user:
            return True
        return super().has_permission()


class RecipientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "newsletter/recipient_form.html"
    success_url = reverse_lazy("newsletter:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def has_permission(self):
        if self.request.user.is_staff and not self.request.user.is_superuser:
            return HttpResponseForbidden("У вас нет прав для добавления новых получателей рассылок")
        return True


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "newsletter/recipient_delete.html"
    success_url = reverse_lazy("newsletter:recipient_list")

    def has_permission(self):
        instance = self.get_object()
        if instance.owner == self.request.user:
            return True
        return HttpResponseForbidden("У вас нет прав для удаления этого получателя")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Получатель успешно удален")
        return super().delete(request, *args, **kwargs)


class RecipientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Recipient
    fields = ["full_name", "email", "comment"]
    template_name = "newsletter/recipient_form.html"
    success_url = reverse_lazy("newsletter:recipient_list")

    def has_permission(self):
        instance = self.get_object()
        if instance.owner == self.request.user:
            return True
        return HttpResponseForbidden("У вас нет прав для редактирования данных этого получателя")


class MailingListView(LoginRequiredMixin, ListView):
    model = MailingList
    template_name = "newsletter/mailing_list.html"
    context_object_name = "mailing_list"

    def get_queryset(self):
        if self.request.user.has_perm("newsletter.can_view_mailing_list"):
            queryset = MailingList.objects.all()
        else:
            queryset = MailingList.objects.filter(owner=self.request.user)
        return queryset

    # def get_queryset(self):
    #     cache_key = f'mailing_list{self.request.user.pk}'
    #     queryset = cache.get(cache_key)
    #     if not queryset:
    #         if self.request.user.has_perm("newsletter.can_view_mailing_list"):
    #             queryset = MailingList.objects.all()
    #         else:
    #             queryset = MailingList.objects.filter(owner=self.request.user)
    #         cache.set(cache_key, queryset, 60 * 5)
    #     return queryset


class MailingDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = MailingList
    template_name = "newsletter/mailing_detail.html"
    context_object_name = "mailing_detail"
    permission_required = "newsletter.can_view_mailing_list"

    def get_context_data(self, *, object_list=None, **kwargs):
        mailing_list = MailingList.objects.get(pk=self.object.pk)
        recipients = mailing_list.recipients.all()
        context = {"mailing_list": mailing_list, "recipient_list": recipients}
        return context

    def has_permission(self):
        instance = self.get_object()
        if instance.owner == self.request.user:
            return True
        return super().has_permission()


class MailingListCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MailingList
    form_class = MailingListForm
    template_name = "newsletter/mailing_form.html"
    success_url = reverse_lazy("newsletter:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["message"].queryset = Message.objects.filter(owner=self.request.user)
        form.fields["recipients"].queryset = Recipient.objects.filter(owner=self.request.user)
        return form

    def has_permission(self):
        if self.request.user.is_staff and not self.request.user.is_superuser:
            return HttpResponseForbidden("У вас нет прав для создания новой рассылки")
        else:
            return True


class MailingListUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingList
    form_class = MailingListForm
    template_name = "newsletter/mailing_edit.html"
    success_url = reverse_lazy("newsletter:mailing_list")

    def get_queryset(self):
        if self.request.user.is_staff:
            return MailingList.objects.all()
        return MailingList.objects.filter(owner=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            form.fields["message"].queryset = Message.objects.filter(owner=self.request.user)
            form.fields["recipients"].queryset = Recipient.objects.filter(owner=self.request.user)
        return form

    def has_permission(self):
        instance = self.get_object()
        if instance.owner == self.request.user or self.request.user.is_superuser:
            return True
        return HttpResponseForbidden("У вас нет прав для редактирования этой рассылки")


class MailingListToggleView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        mailing = get_object_or_404(MailingList, pk=kwargs["pk"])
        if not (request.user.has_perm("newsletter.can_turn_off") or mailing.owner.id == request.user.id):
            raise PermissionDenied("Вы не можете управлять этой рассылкой")
        mailing.is_active = not mailing.is_active
        mailing.save()
        if mailing.is_active and mailing.status == MailingList.CREATED:
            mailing.status = MailingList.STARTED
            mailing.save()
        messages.success(request, f'Рассылка {"включена" if mailing.is_active else "отключена"}')
        return redirect("newsletter:mailing_list")


class MailingListDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingList
    template_name = "newsletter/mailing_confirm_delete.html"
    success_url = reverse_lazy("newsletter:mailing_list")

    def has_permission(self):
        instance = self.get_object()
        if instance.owner == self.request.user or self.request.user.is_superuser:
            return True
        return False


class MailSend(LoginRequiredMixin, View):
    success_url = reverse_lazy("newsletter:home_page")

    def post(self, request, *args, **kwargs):
        mailing_list = get_object_or_404(MailingList, id=self.kwargs["pk"])
        if mailing_list.owner == request.user or request.user.is_superuser or request.user.is_staff:
            mailing_list.send()
        else:
            raise HttpResponseForbidden("У вас нет права запускать эту рассылку")
        return redirect(self.success_url)


class StatisticView(LoginRequiredMixin, TemplateView):
    template_name = "newsletter/statistic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = Statistic.get_statistic(self.request.user)
        context.update(stats)
        return context


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "newsletter/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        cache_key = f'messages_{self.request.user.pk}'
        queryset = cache.get(cache_key)
        if not queryset:
            if self.request.user.has_perm("newsletter.can_view_message"):
                queryset = Message.objects.all()
            else:
                queryset = Message.objects.filter(owner=self.request.user)
            cache.set(cache_key, queryset, 60 * 5)
        return queryset


class MessageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Message
    fields = ["title", "body"]
    template_name = "newsletter/message_form.html"
    success_url = reverse_lazy("newsletter:mailing_create")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def has_permission(self):
        if self.request.user.is_staff and not self.request.user.is_superuser:
            return False
        return True


class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Message
    fields = ["title", "body"]
    template_name = "newsletter/message_form.html"
    success_url = reverse_lazy("newsletter:message_list")

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def has_permission(self):
        instance = self.get_object()
        if instance.owner == self.request.user or self.request.user.is_superuser:
            return True
        return HttpResponseForbidden("У вас нет прав для изменения этого сообщения")


class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Message
    template_name = "newsletter/message_delete.html"
    success_url = reverse_lazy("newsletter:message_list")

    def has_permission(self):
        instance = self.get_object()
        if instance.owner == self.request.user or self.request.user.is_superuser:
            return True
        return HttpResponseForbidden("У вас нет прав для удаления этого сообщения")
