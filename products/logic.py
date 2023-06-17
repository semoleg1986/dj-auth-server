from .models import Seller, Category

def get_seller_by_id(seller_id):
    try:
        seller = Seller.objects.get(id=seller_id)
        return seller
    except Seller.DoesNotExist:
        raise Exception("Продавец с указанным идентификатором не найден.")

def get_category_by_id(category_id):
    try:
        category = Category.objects.get(id=category_id)
        return category
    except Category.DoesNotExist:
        raise Exception("Категория с указанным идентификатором не найдена.")
