# Generated by Django 3.2.19 on 2023-06-17 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_buyer_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_seller',
            field=models.BooleanField(default=False),
        ),
    ]
