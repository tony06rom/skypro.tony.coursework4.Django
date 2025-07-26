from django.contrib import admin

from users.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_active",
        "is_superuser",
        "is_staff",
    )
    list_filter = (
        "email",
        "is_active",
    )
    search_fields = ("username", "email")
