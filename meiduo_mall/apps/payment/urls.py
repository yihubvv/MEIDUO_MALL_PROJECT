from django.urls import path
from apps.payment.views import PaymentView
urlpatterns = [
    path('payment/<order_id>/', PaymentView.as_view()),

]
