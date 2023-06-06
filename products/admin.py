from django.contrib import admin
from .models import Product, Category, OrderItem, Order
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
@admin.register(Order)
class CategoryAdmin(admin.ModelAdmin):
    pass
@admin.register(OrderItem)
class CategoryAdmin(admin.ModelAdmin):
    pass
