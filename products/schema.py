import graphene
from graphene_django import DjangoObjectType
from .models import Seller, Buyer, Product, Category, Order, OrderItem, User

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class SellerType(DjangoObjectType):
    class Meta:
        model = Seller

class BuyerType(DjangoObjectType):
    class Meta:
        model = Buyer

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
    def resolve_category_name(self, info):
        return self.category.name

class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

    status = graphene.String()

    def resolve_status(self, info):
        # Map the status value to the translated string
        status_map = {
            'pending': 'В обработке',
            'accepted': 'Заказ принят',
            'prepare': 'Заказ готовиться',
            'created': 'Заказ готов к выдаче',
            'delivery': 'Передан курьеру',
            'canceled': 'Отменен',
            'completed': 'Выполнен',
            'refunded': 'Возврат',
        }
        return status_map.get(self.status, self.status)

class Query(graphene.ObjectType):
    sellers = graphene.List(SellerType)
    buyers = graphene.List(BuyerType)
    products = graphene.List(ProductType)
    categories = graphene.List(CategoryType)
    orders = graphene.List(OrderType)

    def resolve_sellers(self, info):
        return Seller.objects.all()
    def resolve_buyers(self, info):
        return Buyer.objects.all()
    def resolve_products(self, info):
        return Product.objects.all()
    def resolve_categories(self, info):
        return Category.objects.all()
    def resolve_orders(self, info):
        return Order.objects.all()
class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        # Добавьте другие поля пользователя, если необходимо

    def mutate(self, info, username):
        user = User(username=username)
        user.save()
        return CreateUser(user=user)

class DeleteUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            success = True
        except User.DoesNotExist:
            success = False

        return DeleteUser(success=success)

class CreateSeller(graphene.Mutation):
    seller = graphene.Field(SellerType)

    class Arguments:
        user_id = graphene.Int(required=True)
        phone_number = graphene.String(required=True)
        company_name = graphene.String(required=True)
        description = graphene.String(required=True)

    def mutate(self, info, user_id, phone_number, company_name, description):
        user = User.objects.get(id=user_id)
        seller = Seller(user=user, phone_number=phone_number, company_name=company_name, description=description)
        seller.save()
        return CreateSeller(seller=seller)

class UpdateBuyer(graphene.Mutation):
    class Arguments:
        buyer_id = graphene.ID(required=True)
        phone_number = graphene.String()
        name = graphene.String()
        surname = graphene.String()
        address = graphene.String()
        email = graphene.String()

    buyer = graphene.Field(BuyerType)

    def mutate(self, info, buyer_id, **kwargs):
        try:
            buyer = Buyer.objects.get(id=buyer_id)
            for key, value in kwargs.items():
                setattr(buyer, key, value)
            buyer.save()
        except Buyer.DoesNotExist:
            buyer = None

        return UpdateBuyer(buyer=buyer)


class CreateBuyer(graphene.Mutation):
    buyer = graphene.Field(BuyerType)

    class Arguments:
        user_id = graphene.Int(required=True)
        phone_number = graphene.String(required=True)
        name = graphene.String(required=True)
        surname = graphene.String(required=True)
        address = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, user_id, phone_number, name, surname, address, email):
        user = User.objects.get(id=user_id)
        buyer = Buyer(user=user, phone_number=phone_number, name=name, surname=surname, address=address, email=email)
        buyer.save()
        return CreateBuyer(buyer=buyer)

class UpdateSeller(graphene.Mutation):
    class Arguments:
        seller_id = graphene.ID(required=True)
        phone_number = graphene.String()
        company_name = graphene.String()
        description = graphene.String()

    seller = graphene.Field(SellerType)

    def mutate(self, info, seller_id, **kwargs):
        try:
            seller = Seller.objects.get(id=seller_id)
            for key, value in kwargs.items():
                setattr(seller, key, value)
            seller.save()
        except Seller.DoesNotExist:
            seller = None

        return UpdateSeller(seller=seller)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        quantity = graphene.Int(required=True)
        category_id = graphene.ID(required=True)
        seller_id = graphene.ID(required=True)  # Добавленное поле seller_id

    product = graphene.Field(ProductType)

    def mutate(self, info, name, description, price, quantity, category_id, seller_id):
        category = Category.objects.get(pk=category_id)
        seller = Seller.objects.get(pk=seller_id)  # Получение объекта продавца по seller_id
        product = Product(name=name, description=description, price=price, quantity=quantity, category=category, seller=seller)  # Установка связи продавца
        product.save()
        return CreateProduct(product=product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        price = graphene.Decimal()
        quantity = graphene.Int()
        category_id = graphene.ID()

    product = graphene.Field(ProductType)

    def mutate(self, info, id, name=None, description=None, price=None, quantity=None, category_id=None):
        product = Product.objects.get(pk=id)
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if quantity is not None:
            product.quantity = quantity
        if category_id is not None:
            category = Category.objects.get(pk=category_id)
            product.category = category
        product.save()
        return UpdateProduct(product=product)


class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        product = Product.objects.get(pk=id)
        product.delete()
        return DeleteProduct(success=True)

class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    def mutate(self, info, name):
        category = Category(name=name)
        category.save()
        return CreateCategory(category=category)
class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    category = graphene.Field(CategoryType)

    def mutate(self, info, id, name):
        category = Category.objects.get(pk=id)
        category.name = name
        category.save()
        return UpdateCategory(category=category)

class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        category = Category.objects.get(pk=id)
        category.delete()
        return DeleteCategory(success=True)
class CreateOrder(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        surname = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        address = graphene.String(required=True)
        email = graphene.String(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        quantities = graphene.List(graphene.Int, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, name, surname, phone_number, address, email, product_ids, quantities):
        order = Order(
            name=name,
            surname=surname,
            phone_number=phone_number,
            address=address,
            email=email,
        )
        order.save()

        for product_id, quantity in zip(product_ids, quantities):
            product = Product.objects.get(pk=product_id)
            order_item = OrderItem(order=order, product=product, quantity=quantity)
            order_item.save()

        return CreateOrder(order=order)

class UpdateOrder(graphene.Mutation):
    class Arguments:
        order_id = graphene.ID(required=True)
        name = graphene.String()
        surname = graphene.String()
        phone_number = graphene.String()
        address = graphene.String()
        status = graphene.String()

    order = graphene.Field(OrderType)

    def mutate(self, info, order_id, name=None, surname=None, phone_number=None, address=None, status=None):
        order = Order.objects.get(pk=order_id)
        if name is not None:
            order.name = name
        if surname is not None:
            order.surname = surname
        if phone_number is not None:
            order.phone_number = phone_number
        if address is not None:
            order.address = address
        if status is not None:
            order.status = status
        order.save()
        return UpdateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()
    create_order = CreateOrder.Field()
    update_order = UpdateOrder.Field()
    create_user = CreateUser.Field()
    delete_user = DeleteUser.Field()
    create_seller = CreateSeller.Field()
    update_seller = UpdateSeller.Field()
    create_buyer = CreateBuyer.Field()
    update_buyer = UpdateBuyer.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
