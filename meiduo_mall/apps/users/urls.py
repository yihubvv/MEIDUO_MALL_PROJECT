from django.urls import path
from apps.users.views import UsernameCountView, RegisterView
urlpatterns = [
    #Check whether the username already exists.
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('register/',RegisterView.as_view())

]