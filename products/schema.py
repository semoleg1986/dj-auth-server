from django.contrib.auth import authenticate, login
import graphene
from graphene_django import DjangoObjectType
from .models import Seller, Buyer, Product, Category, Order, OrderItem, User
from graphql_jwt.shortcuts import get_token
import channels_graphql_ws
import channels
# import channels.layers
# from asgiref.sync import async_to_sync

# def broadcast(group_name, payload):
#     channel_layer = channels.layers.get_channel_layer()
#     async_to_sync(channel_layer.group_send)(group_name, payload)

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

def get_orders_by_seller_id(seller_id):
    # Получаем все заказы, связанные с данным идентификатором продавца
    orders = Order.objects.filter(seller_id=seller_id)

    return orders

class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    sellers = graphene.List(SellerType)

    buyers = graphene.List(BuyerType)
    buyer_by_id = graphene.Field(BuyerType, buyer_id=graphene.ID(required=True))

    products = graphene.List(ProductType)
    products_by_seller_id = graphene.List(ProductType, seller_id=graphene.ID(required=True))

    categories = graphene.List(CategoryType)

    orders = graphene.List(OrderType)
    orders_by_buyer_id = graphene.List(OrderType,
    buyer_id=graphene.ID(required=True))
    orders_by_status = graphene.List(OrderType, status=graphene.String(required=True))

    orders_by_seller_id = graphene.List(OrderType, seller_id=graphene.ID(required=True))

    statuses = graphene.List(graphene.String)

    def resolve_statuses(self, info):
        return ['pending', 'accepted','prepare', 'created', 'delivery', 'canceled', 'completed', 'refunded',]
    def resolve_products_by_seller_id(self, info, seller_id):
        return Product.objects.filter(seller__id=seller_id)
    def resolve_buyer_by_id(self, info, buyer_id):
        try:
            return Buyer.objects.get(pk=buyer_id)
        except Buyer.DoesNotExist:
            return None
    def resolve_orders_by_buyer_id(self, info, buyer_id):
        try:
            return Order.objects.filter(buyer_id=buyer_id)
        except Order.DoesNotExist:
            return None
    def resolve_orders_by_status(self, info, status):
        return Order.objects.filter(status=status)
    def resolve_orders_by_seller_id(self, info, seller_id):
        try:
            return Order.objects.filter(seller_id=seller_id)
        except Order.DoesNotExist:
            return None

    def resolve_users(self, info):
        return User.objects.all()
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
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = User(username=username)
        user.set_password(password)  # Установка пароля
        user.save()
        return CreateUser(user=user)

class LoginUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()
    user = graphene.Field(UserType)

    @staticmethod
    def mutate(root, info, username, password):
        user = authenticate(username=username, password=password)

        if user is None or not user.is_active:
            raise Exception('Invalid credentials')

        login(info.context, user)
        token = get_token(user)

        return LoginUser(token=token, user=user)

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
        user_id = graphene.ID(required=True)
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
        user_id = graphene.ID(required=True)
        phone_number = graphene.String(required=True)
        name = graphene.String(required=True)
        surname = graphene.String(required=True)

    def mutate(self, info, user_id, phone_number, name, surname):
        user = User.objects.get(id=user_id)
        buyer = Buyer(user=user, phone_number=phone_number, name=name, surname=surname)
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
    def broadcast(self, group_name, payload):
        self.broadcast(group_name, payload)
    def mutate(self, info, id):
        category = Category.objects.get(pk=id)
        category.delete()
        return DeleteCategory(success=True)
class OrderSubscription(channels_graphql_ws.Subscription):
    order = graphene.Field(OrderType)
    class Arguments:
        seller_id = graphene.ID(required=True)

    order_status = graphene.String()
    def subscribe(self, info, seller_id):
        # Проверяем, аутентифицирован ли пользователь и является ли он продавцом с указанным идентификатором
        user = info.context.user
        if user.is_authenticated and user.is_seller and user.id == int(seller_id):
            # Создание уникальной группы каналов для данного продавца
            group_name = f'seller_{user.id}'
            self.groups.append(group_name)
            return [group_name]
        return None

    def publish(payload,info, seller_id):
        return OrderSubscription(seller_id, payload)



    def unsubscribe(self, info, seller_id):
        # Проверяем, аутентифицирован ли пользователь и является ли он продавцом с указанным идентификатором
        user = info.context.user
        if user.is_authenticated and user.is_seller and user.id == int(seller_id):
            group_name = f'seller_{user.id}'
            self.groups.remove(group_name)
            return True
        return False

class CreateOrder(graphene.Mutation):
    class Arguments:
        seller_id = graphene.ID(required=True)
        buyer_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        surname = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        address = graphene.String(required=True)
        email = graphene.String(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        quantities = graphene.List(graphene.Int, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, seller_id, buyer_id, name, surname, phone_number, address, email, product_ids, quantities):
        seller = Seller.objects.get(pk=seller_id)
        buyer = Buyer.objects.get(pk=buyer_id)
        order = Order(
            name=name,
            surname=surname,
            phone_number=phone_number,
            address=address,
            email=email,
            seller=seller,
            buyer=buyer,
        )
        order.save()

        for product_id, quantity in zip(product_ids, quantities):
            product = Product.objects.get(pk=product_id)
            order_item = OrderItem(order=order, product=product, quantity=quantity)
            order_item.save()

        OrderSubscription.broadcast(payload={
            'order_id': str(order.id),
            'new_status': order.status,
        })
        # OrderSubscription.broadcast(payload=payload)

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
    update_order_status = graphene.Field(OrderType, order_id=graphene.ID(required=True), status=graphene.String(required=True))
    create_user = CreateUser.Field()
    login_user = LoginUser.Field()
    delete_user = DeleteUser.Field()
    create_seller = CreateSeller.Field()
    update_seller = UpdateSeller.Field()
    create_buyer = CreateBuyer.Field()
    update_buyer = UpdateBuyer.Field()

    def resolve_update_order_status(self, info, order_id, status):
        try:
            order = Order.objects.get(pk=order_id)
            order.status = status
            order.save()
            return order
        except Order.DoesNotExist:
            return  Exception("Order not found")




class Subscription(graphene.ObjectType):
    order_updates = OrderSubscription.Field()

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)

def demo_middleware(next_middleware, root, info, *args, **kwds):
    if (
        info.operation.name is not None
        and info.operation.name.value != "IntrospectionQuery"
    ):
        print("Demo middleware report")
        print("    operation :", info.operation.operation)
        print("    name      :", info.operation.name.value)

    # Invoke next middleware.
    result = next_middleware(root, info, *args, **kwds)
    return result

class MyGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    async def on_connect(self, payload):
        self.scope["user"] = await channels.auth.get_user(self.scope)
    schema = schema
    middleware = [demo_middleware]
