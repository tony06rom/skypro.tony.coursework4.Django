import secrets

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm
from users.models import User


class UserRegisterView(CreateView):
    model = User
    template_name = "users/user_register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:user_login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}"
        try:
            send_mail(
                subject="Подтверждение регистрации",
                message=f"Здравствуйте! Пройдите по ссылке для подтверждения регистрации\n{url}",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
        except Exception as e:
            print(f"Ошибка отправки письма: {e}")
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:user_login"))


class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')
    success_message = "Письмо для сброса пароля отправлено на ваш email"

    def form_valid(self, form):
        if not User.objects.filter(email=form.cleaned_data['email']).exists():
            form.add_error('email', 'Пользователя с таким email не существует в системе')
            return self.form_invalid(form)
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('users:password_reset_complete')
    success_message = "Пароль успешно изменен. Авторизуйтесь с новым паролем."


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
