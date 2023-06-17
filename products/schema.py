import strawberry
from datetime import datetime
from django.contrib.auth import authenticate, login
from typing import List
from .models import Seller, Buyer, Category, Product, Order, OrderItem, User
from strawberry_jwt_auth.extension import JWTExtension
from graphql_jwt.shortcuts import get_token
from .logic import get_seller_by_id, get_category_by_id, get_buyer_by_id, get_product_by_id,get_orders_by_seller_id
import asyncio


@strawberry.type
class UserType:
    id: strawberry.ID
    username: str
    created_at: str

@strawberry.type
class LoginResponse:
    user: UserType
    token: str

@strawberry.type
class SellerType:
    id: strawberry.ID
    user: UserType
    phone_number: str
    company_name: str
    created_at: str
    updated_at: str

@strawberry.type
class BuyerType:
    id: strawberry.ID
    user: UserType
    phone_number: str
    name: str
    surname: str
    address: str
    created_at: str
    updated_at: str

@strawberry.type
class CategoryType:
    id: strawberry.ID
    name: str

@strawberry.type
class ProductType:
    id: strawberry.ID
    seller: SellerType
    name: str
    description: str
    price: float
    quantity: int
    category: CategoryType
    created_at: str
    updated_at: str

@strawberry.type
class OrderItemType:
    id: strawberry.ID
    product: ProductType
    quantity: int

@strawberry.type
class OrderType:
    id: strawberry.ID
    buyer: BuyerType
    seller: SellerType
    order_number: str
    receipt_number: str
    name: str
    surname: str
    phone_number: str
    address: str
    email: str
    status: str
    update_date: str
    products: List[OrderItemType]
    created_at: str

@strawberry.input
class LoginInput:
    username: str
    password: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> SellerType:
        return User.objects.first()

    @strawberry.field
    def seller(self) -> SellerType:
        return Seller.objects.first()

    @strawberry.field
    def buyer(self) -> BuyerType:
        return Buyer.objects.first()

    @strawberry.field
    def category(self, category_id: int) -> CategoryType:
        return Category.objects.get(id=category_id)

    @strawberry.field
    def product(self, product_id: int) -> ProductType:
        return Product.objects.get(id=product_id)

    @strawberry.field
    def order(self, order_id: int) -> OrderType:
        return Order.objects.get(id=order_id)

    @strawberry.field
    def users(self) -> List[UserType]:
        return User.objects.all()

    @strawberry.field
    def sellers(self) -> List[SellerType]:
        return Seller.objects.all()

    @strawberry.field
    def buyers(self) -> List[BuyerType]:
        return Buyer.objects.all()

    @strawberry.field
    def products(self) -> List[ProductType]:
        return Product.objects.all()

    @strawberry.field
    def products_by_seller_id(self, seller: strawberry.ID) -> List[ProductType]:
        return Product.objects.filter(seller=seller)

    @strawberry.field
    def categories(self) -> List[CategoryType]:
        return Category.objects.all()

    @strawberry.field
    def orders(self) -> List[OrderType]:
        return Order.objects.all()

    @strawberry.field
    def orders_by_buyer_id(self, buyer: strawberry.ID) -> List[OrderType]:
        return Order.objects.filter(buyer=buyer)

    @strawberry.field
    def orders_by_seller_id(self, seller: strawberry.ID) -> List[OrderType]:
        return Order.objects.filter(seller=seller)

@strawberry.subscription
async def order_seller_subscription(seller_id: strawberry.ID) -> OrderType:
    # Создаем асинхронный генератор, который будет посылать обновления о заказах продавца
    while True:
        # Получаем список заказов продавца по его идентификатору
        orders = get_orders_by_seller_id(seller_id)

        # Отправляем каждый заказ в качестве обновления подписчику
        for order in orders:
            yield order

        # Ждем некоторое время перед отправкой следующих обновлений
        await asyncio.sleep(5)  # Например, отправляем обновления каждые 5 секунд

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(
        self,
        username: str,
        password: str,
    ) -> UserType:
        user = User.objects.create_user(
            username=username,
            password=password,
        )
        return user
    @strawberry.mutation
    def login(self, info, username: str, password: str) -> LoginResponse:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Exception("Пользователь с указанным адресом электронной почты не существует.")

        if user.check_password(password):
            token = get_token(user)
            return LoginResponse(user=UserType(id=str(user.id), username=user.username, created_at=str(user.created_at)), token=token)
        else:
            raise Exception("Неверный пароль.")

    @strawberry.mutation
    def create_seller(
        user_id: strawberry.ID,
        phone_number: str,
        company_name: str,
    ) -> SellerType:
        user = User.objects.get(id=user_id)
        seller = Seller.objects.create(user=user, phone_number=phone_number, company_name=company_name)
        return seller

    @strawberry.mutation
    def create_buyer(
        user_id: strawberry.ID,
        phone_number: str,
        name: str,
        surname: str,
        address: str,
    ) -> BuyerType:
        user = User.objects.get(id=user_id)
        buyer = Buyer.objects.create(user=user,phone_number=phone_number,
        name = name,
        surname = surname,
        address = address,)
        return buyer

    @strawberry.mutation
    def create_product(
        info,
        seller_id: strawberry.ID,
        name: str,
        description: str,
        price: float,
        quantity: int,
        category_id: strawberry.ID
    ) -> ProductType:
        seller = get_seller_by_id(seller_id)
        category = get_category_by_id(category_id)
        product = Product(
            seller=seller,
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            category=category
        )
        product.save()
        return ProductType(
            id=str(product.id),
            seller=seller,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            created_at=str(product.created_at),
            updated_at=str(product.updated_at),
            category=category
        )

    @strawberry.mutation
    def update_product(info, id: strawberry.ID, name: str, description: str, price: float, quantity: int, category_id: strawberry.ID) -> ProductType:
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Exception("Продукт с указанным идентификатором не найден.")
        product.name = name
        product.description = description
        product.price = price
        product.quantity = quantity
        product.category = get_category_by_id(category_id)
        product.updated_at = datetime.now()
        product.save()
        return ProductType(
            id=str(product.id),
            seller=product.seller,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            created_at=str(product.created_at),
            updated_at=str(product.updated_at),
            category=product.category
        )
    @strawberry.mutation
    def delete_product(info, id: strawberry.ID) -> bool:
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Exception("Продукт с указанным идентификатором не найден.")
        product.delete()
        return True
    @strawberry.mutation
    def create_category(info, name: str) -> CategoryType:
        category = Category(
            name=name,
        )
        category.save()
        return CategoryType(
            id=category.id,
            name=category.name,
        )

    @strawberry.mutation
    def update_category(info, id: strawberry.ID, name: str) -> CategoryType:
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise Exception("Категория с указанным идентификатором не найдена.")
        category.name = name
        category.save()
        return CategoryType(
            id=str(category.id),
            name=category.name,
        )
    @strawberry.mutation
    def delete_category(info, id: strawberry.ID) -> bool:
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise Exception("Продукт с указанным идентификатором не найден.")
        category.delete()
        return True

    @strawberry.mutation
    def create_order(
        info,
        buyer_id: strawberry.ID,
        seller_id: strawberry.ID,
        name: str,
        surname: str,
        phone_number: str,
        address: str,
        email: str,
        products: List[strawberry.ID],
        quantities: List[int],
    ) -> OrderType:
        # Получение объектов покупателя и продавца по их идентификаторам
        buyer = get_buyer_by_id(buyer_id)
        seller = get_seller_by_id(seller_id)

        # Создание нового заказа
        order = Order(
            buyer=buyer,
            seller=seller,
            name=name,
            surname=surname,
            phone_number=phone_number,
            address=address,
            email=email,
        )
        order.save()

        # Добавление продуктов к заказу
        for product_id, quantity in zip(products, quantities):
            product = get_product_by_id(product_id)
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        # Возвращение созданного заказа
        return OrderType(
            id=str(order.id),
            buyer=buyer,
            seller=seller,
            order_number=str(order.order_number),
            receipt_number=order.receipt_number,
            name=order.name,
            surname=order.surname,
            phone_number=order.phone_number,
            address=order.address,
            email=order.email,
            status=order.status,
            update_date=str(order.update_date),
            created_at=str(order.created_at),
            products=[
                OrderItemType(
                    id=str(item.id),
                    product=item.product,
                    quantity=item.quantity,
                )
                for item in order.orderitem_set.all()
            ],
        )

@strawberry.type
class Subscription:
    order_seller = order_seller_subscription




schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription, extensions = [
        JWTExtension,
    ])
