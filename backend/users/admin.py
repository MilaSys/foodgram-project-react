from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Настройки отображения таблицы с пользователями в админ зоне.
    Attributes:
        list_display: - отображаемые поля
        search_fields: - поле для поиска соответствий
        list_filter: - сортируемое поле записей
        list_editable: - редактируемое поле
        empty_value_display: - заполнитель ячеек со значением None
    """

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'date_joined',
        'is_active',
        'password',
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_active',
    )
    list_filter = (
        'email',
        'first_name',
        'is_active',
    )
    list_editable = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'password',
    )
    empty_value_display = '-пусто-'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
