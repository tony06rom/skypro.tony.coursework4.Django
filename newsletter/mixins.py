from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin

from users.models import Profile


class OwnerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь - владелец объекта."""
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user or self.request.user.profile.role == Profile.MANAGER

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для выполнения этого действия.")

class ManagerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь - менеджер."""
    def test_func(self):
        return self.request.user.profile.role == Profile.MANAGER

    def handle_no_permission(self):
        raise PermissionDenied("Только менеджеры могут выполнять это действие.")