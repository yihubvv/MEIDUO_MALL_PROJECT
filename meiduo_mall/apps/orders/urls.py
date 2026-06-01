from django.urls import path
from apps.orders.views import OrderSettlementView
urlpatterns = [
    #Check whether the username already exists.
    path('orders/settlement/',OrderSettlementView.as_view()),
]