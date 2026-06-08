from django.urls import path
from apps.carts.views import CartsSelectAllView, CartsView,CartsSimpleView

urlpatterns = [
  path('carts/',CartsView.as_view()),
  path('carts/selection/',CartsSelectAllView.as_view()),
  path('carts/simple/',CartsSimpleView.as_view()),
]
