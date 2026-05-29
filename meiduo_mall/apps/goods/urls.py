from django.urls import path
from apps.goods.views import IndexView

urlpatterns = [
  path('index/',IndexView.as_view())
]