import graphene
from graphene_django import DjangoObjectType
from .models import Product

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class Query(graphene.ObjectType):
    products = graphene.List(ProductType)

    def resolve_products(self, info):
        return Product.objects.all()
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        quantity = graphene.Int(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, description, price, quantity):
        product = Product(name=name, description=description, price=price, quantity=quantity)
        product.save()
        return CreateProduct(product=product)

class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        price = graphene.Decimal()
        quantity = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, id, name=None, description=None, price=None, quantity=None):
        product = Product.objects.get(pk=id)
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if quantity is not None:
            product.quantity = quantity
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

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
