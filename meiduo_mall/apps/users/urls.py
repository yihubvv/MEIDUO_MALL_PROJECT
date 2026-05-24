from django.urls import path
from apps.users.views import UsernameCountView
urlpatterns = [
    #Check whether the username already exists.
    path('usernames/<username>/count/',UsernameCountView.as_view()),

]