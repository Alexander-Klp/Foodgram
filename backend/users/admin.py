from django.contrib import admin

from api.forms import CustomUserChangeForm
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'
