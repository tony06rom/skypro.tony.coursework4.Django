from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import UserRegisterView, email_verification

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/user_login.html"), name="user_login"),
    path("logout/", LogoutView.as_view(template_name="users/user_logout.html", next_page="/newsletter/home_page"), name="user_logout"),
    path("register/", UserRegisterView.as_view(template_name="users/user_register.html"), name="user_register"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
]
