from django.contrib import admin
from .models import Item, Order, OrderItem, Payment, Coupon, BillingAddress, Refund


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['id', 'slug', 'title', 'price', 'discount_price', 'category', 'image']

    save_as = True
    save_on_top = True


admin.site.register(Item, ItemAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(BillingAddress)
admin.site.register(Refund)
