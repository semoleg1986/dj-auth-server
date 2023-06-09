# Generated by Django 4.2.1 on 2023-06-06 15:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_category_product_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("order_number", models.UUIDField(editable=False, unique=True)),
                (
                    "receipt_number",
                    models.CharField(editable=False, max_length=7, unique=True),
                ),
                ("name", models.CharField(max_length=100)),
                ("surname", models.CharField(max_length=100)),
                ("phone_number", models.CharField(max_length=20)),
                ("address", models.TextField()),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        validators=[django.core.validators.EmailValidator()],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "В обработке"),
                            ("accepted", "Заказ принят"),
                            ("prepare", "Заказ готовиться"),
                            ("created", "Заказ готов к выдаче"),
                            ("delivery", "Передан курьеру"),
                            ("canceled", "Отменен"),
                            ("completed", "Выполнен"),
                            ("refunded", "Возврат"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("update_date", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name="category",
            options={
                "ordering": ("name",),
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField()),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="products.order"
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.product",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="products",
            field=models.ManyToManyField(
                through="products.OrderItem", to="products.product"
            ),
        ),
    ]
