from .models import Seller, Category,  Buyer, Product, Order

def get_seller_by_id(seller_id):
    try:
        seller = Seller.objects.get(id=seller_id)
        return seller
    except Seller.DoesNotExist:
        raise Exception("Продавец с указанным идентификатором не найден.")

def get_buyer_by_id(buyer_id):
    try:
        buyer = Buyer.objects.get(id=buyer_id)
        return buyer
    except Buyer.DoesNotExist:
        raise Exception("Покупатель с указанным идентификатором не найден.")

def get_category_by_id(category_id):
    try:
        category = Category.objects.get(id=category_id)
        return category
    except Category.DoesNotExist:
        raise Exception("Категория с указанным идентификатором не найдена.")

def get_product_by_id(product_id):
    try:
        product = Product.objects.get(id=product_id)
        return product
    except Product.DoesNotExist:
        raise Exception("Продукт с указанным идентификатором не найдена.")

def get_orders_by_seller_id(seller_id: int):
    try:
        seller = Seller.objects.get(id=seller_id)
        orders = Order.objects.filter(seller=seller)
        return orders
    except Seller.DoesNotExist:
        # Обработка случая, когда продавец с указанным идентификатором не найден
        raise Exception("Продавец с указанным идентификатором не найден.")
