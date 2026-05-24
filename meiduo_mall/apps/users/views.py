from django.shortcuts import render

# Create your views here.
"""
Requirement Analysis: Based on the page functionality (from top to bottom, left to right), determine which features need backend interaction.

How do we determine which features need to interact with the backend?
    1. Experience
    2. Observe similar features on similar websites

"""

"""
Function: Check whether the username already exists.

Frontend (understanding):
    When the user enters a username and the input loses focus,
    send an axios (ajax) request.

Backend (logic):
    Request:
        Receive the username

    Business Logic:
        Query the database based on the username.
        If the query result count equals 0, it means the username is not registered.
        If the query result count equals 1, it means the username is already registered.

    Response:
        JSON
        {code:0,count:0/1,errmsg:ok}

    Route:
        GET usernames/<username>/count/

Steps:
    1. Receive the username
    2. Query the database based on the username
    3. Return the response

"""
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
import re
class UsernameCountView(View):

def get(self, request, username):
    # 1. Receive the username and validate it
    # if not re.match('[a-zA-Z0-9_-]{5,20}', username):
    #     return JsonResponse({'code': 200, 'errmsg': 'Username does not meet the requirements'})

    # 2. Query the database based on the username
    count = User.objects.filter(username=username).count()

    # 3. Return the response
    return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})

