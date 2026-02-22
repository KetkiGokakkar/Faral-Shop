# shop/admin.py
from django.contrib import admin
from .models import Category, Product, Customer, Address, Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'unit_price')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_amount', 'status', 'placed_at')
    list_filter = ('status', 'placed_at')
    search_fields = ('customer__phone', 'customer__name')
    inlines = [OrderItemInline]
    readonly_fields = ('placed_at',)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Payment)
