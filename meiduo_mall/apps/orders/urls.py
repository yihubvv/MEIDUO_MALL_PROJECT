from django.urls import path
from apps.orders.views import OrderCommitView,OrderSettlementView
urlpatterns = [
    #Check whether the username already exists.
    path('orders/settlement/',OrderSettlementView.as_view()),
    path('orders/commit/',OrderCommitView.as_view()),
]