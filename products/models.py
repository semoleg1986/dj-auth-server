from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid
from django.core.validators import EmailValidator
import secrets
import string

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('accepted', 'Заказ принят'),
        ('prepare', 'Заказ готовиться'),
        ('created', 'Заказ готов к выдаче'),
        ('delivery', 'Передан курьеру'),
        ('canceled', 'Отменен'),
        ('completed', 'Выполнен'),
        ('refunded', 'Возврат'),
    )

    order_number = models.UUIDField(unique=True, editable=False)
    receipt_number = models.CharField(max_length=7, unique=True, editable=False)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    email = models.EmailField(validators=[EmailValidator()], blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    update_date = models.DateTimeField(auto_now=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order #{self.pk}"

@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance, **kwargs):
    if not instance.order_number:
        instance.order_number = uuid.uuid4()

@receiver(pre_save, sender=Order)
def generate_receipt_number(sender, instance, **kwargs):
    if not instance.receipt_number:
        receipt_number = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))
        instance.receipt_number = receipt_number

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
