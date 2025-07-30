from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import UserRegisterView, email_verification, CustomPasswordResetView, CustomPasswordResetDoneView, \
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, UserListView, UserUpdateView, UserDeleteView

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/user_login.html"), name="user_login"),
    path("logout/", LogoutView.as_view(template_name="users/user_logout.html", next_page="/newsletter/home_page"), name="user_logout"),
    path("register/", UserRegisterView.as_view(template_name="users/user_register.html"), name="user_register"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset/<uidb64>/<str:token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset/complete/", CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("users/", UserListView.as_view(), name="users_list"),
    path('profile/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('profile/delete/', UserDeleteView.as_view(), name='user_delete'),
]
