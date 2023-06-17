from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView
from strawberry_jwt_auth.views import strawberry_auth_view
from .schema import schema

urlpatterns = [
    # Other URL patterns
    path('graphql/', csrf_exempt(strawberry_auth_view(GraphQLView.as_view(graphiql=True, schema=schema)))),
]
