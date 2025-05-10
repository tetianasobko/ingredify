from django.contrib import admin

from shopping_list.models import ShoppingList


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__email",)
    ordering = ("user",)
