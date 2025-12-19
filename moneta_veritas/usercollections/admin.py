# usercollections/admin.py
from django.contrib import admin
from .models import UserCollectionItem


@admin.register(UserCollectionItem)
class UserCollectionItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_item_name', 'get_item_type', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__username', 'coin__name', 'banknote__name', 'notes')
    readonly_fields = ('added_at',)

    def get_item_name(self, obj):
        return obj.get_item().name

    get_item_name.short_description = 'Название предмета'

    def get_item_type(self, obj):
        return 'Монета' if obj.coin else 'Банкнота'

    get_item_type.short_description = 'Тип'

    def has_add_permission(self, request):
        # Разрешаем добавлять только через интерфейс сайта
        return False