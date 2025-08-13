from django.contrib.auth.forms import UserCreationForm

from newsletter.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = [
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "city",
            "phone_number",
            "avatar",
        ]
