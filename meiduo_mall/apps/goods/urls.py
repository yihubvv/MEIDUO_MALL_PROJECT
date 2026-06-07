from django.urls import path
from apps.goods.views import IndexView, ListView,SKUSearchView, DetailView, CategoryVisitCountView,HotGoodsView
from haystack.views import search_view_factory

urlpatterns = [
  path('index/',IndexView.as_view()),
  path('lists/<category_id>/skus/',ListView.as_view()),
  path('hot/<category_id>/',HotGoodsView.as_view()),
  path('search/',search_view_factory(view_class=SKUSearchView)),
  path('detail/<sku_id>/',DetailView.as_view()),
  path('detail/visit/<category_id>/',CategoryVisitCountView.as_view()),
]
