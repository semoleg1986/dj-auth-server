from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Product, Category, OrderItem, Order, Seller, Buyer
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass
@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    pass
@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    pass
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(User, UserAdmin)
