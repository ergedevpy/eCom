from django.contrib import admin
from .models import Item


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    save_as = True
    save_on_top = True


admin.site.register(Item, ItemAdmin)
