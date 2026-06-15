from django.urls import path

from apps.contents.views import ContentListView


urlpatterns = [
    path('contents/<key>/', ContentListView.as_view()),
]
