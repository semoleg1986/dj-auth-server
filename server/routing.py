from django.urls import re_path
from products.schema import MyGraphqlWsConsumer

websocket_urlpatterns = [
    re_path('graphql/', MyGraphqlWsConsumer.as_asgi()),
]
