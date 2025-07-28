from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="e-mail", help_text="Введите e-mail")
    first_name = models.CharField(max_length=50, verbose_name="Имя", help_text="Введите имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия", help_text="Введите фамилию")
    phone_number = models.CharField(max_length=50, verbose_name="Номер телефона", help_text="Введите телефон")
    city = models.CharField(max_length=50, verbose_name="Город", help_text="Ваш город")
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, verbose_name="Аватар", help_text="Загрузите аватар"
    )
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True, help_text="Последний вход")
    is_active = models.BooleanField(default=True, blank=True, null=True, help_text="Статус УЗ")
    token = models.CharField(max_length=100, verbose_name="Токен", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number", "city"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
