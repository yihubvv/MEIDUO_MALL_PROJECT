from math import log

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
from django.http import HttpRequest, JsonResponse
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
    
class MobileView(View):

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'count': count, 'errmsg': 'ok'})
    
import json
from django.contrib.auth import login,authenticate
class RegisterView(View):

    def post(self, request:HttpRequest):
        req = request.body.decode()
        req_dict = json.loads(req)
        allow = req_dict['allow']
        mobile = req_dict['mobile']
        password = req_dict['password']
        password2 = req_dict['password2']
        # sms_code = req_dict['sms_code']
        username_req = req_dict['username']
        
        if not all([allow,mobile,password,password2,username_req]):
            return JsonResponse({'code':400, 'errmsg':'incomplete data'})
        
        if not (allow == True):
            return JsonResponse({'code':400, 'errmsg':'User does not agree to the agreement.'})
        
        if not re.match(r'[a-zA-Z_-]{5,20}',username_req):
            return JsonResponse({'code':400, 'errmsg':'User name should be 5-20 characters.'})
        
        if not (User.objects.filter(username=username_req).count() == 0):
            return JsonResponse({'code':400, 'errmsg':'Duplicate username.'})

        if not (re.match(r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$', mobile)):
            return JsonResponse({'code':400, 'errmsg':'Bad phone number.'})
        
        if not (User.objects.filter(mobile=mobile).count() == 0):
            return JsonResponse({'code':400, 'errmsg':'Duplicate phone number.'})

        if not (len(password) > 8 or len(password) < 20):
            return JsonResponse({'code':400, 'errmsg':'Bad password.'})
        
        if not (password == password2):
            return JsonResponse({'code':400, 'errmsg':'Passwords do not match.'})
        
        user = User.objects.create_user(username=username_req, password=password, mobile=mobile)

        login(request,user)
        
        return JsonResponse({'code':0, 'errmsg':'Success'})
    
class LoginView(View):
    def post(self,request:HttpRequest):
        data = json.loads(request.body.decode())
        v_username = data['username']
        v_password = data['password']
        v_remembered = data['remembered']

        if not all([v_username,v_password]):
            return JsonResponse({'code':400,'errmsg':'Incomplete Data.'})
        
        user = authenticate(username=v_username,password=v_password)

        if(user == None):
            return JsonResponse({'code':400,'errmsg':'Incorrect Username/Password.'})

        login(request,user)

        if(v_remembered != None):
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        
        return JsonResponse({'code':0,'errmsg':'OK'})
