from django.urls import path

from main.consumers import ListenToProcessResultsConsumer


websocket_urlpatterns = [
    path('ws/listen/<str:ip>/', ListenToProcessResultsConsumer.as_asgi()),
]
