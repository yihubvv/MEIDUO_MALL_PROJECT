from django.urls import path
from apps.users.views import UsernameCountView, RegisterView, MobileView,LoginView,LogoutView,CenterView,EmailView
urlpatterns = [
    #Check whether the username already exists.
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('register/',RegisterView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('info/',CenterView.as_view()),
    path('emails/',EmailView.as_view()),
    path('mobiles/<mobile:mobile>/count/', MobileView.as_view())

]