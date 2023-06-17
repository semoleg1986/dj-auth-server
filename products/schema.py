import strawberry
from django.contrib.auth import authenticate, login
from typing import List
from .models import Seller, Buyer, Category, Product, Order, OrderItem, User
from strawberry_jwt_auth.extension import JWTExtension
from graphql_jwt.shortcuts import get_token
from .logic import get_seller_by_id, get_category_by_id

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
    order: "OrderType"
    product: ProductType
    quantity: int

@strawberry.type
class OrderType:
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
        # Создание нового продукта
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
        return product

        # Возвращение созданного продукта
        return ProductType(
            id=str(product.id),
            seller=seller,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            category=category
        )
    @strawberry.mutation
    def create_category(info, name: str) -> CategoryType:
        # Создание новой категории
        category = Category(
            name=name,
        )
        category.save()
        return CategoryType(
            name=category.name,
        )

schema = strawberry.Schema(query=Query, mutation=Mutation, extensions = [
        JWTExtension,
    ])
