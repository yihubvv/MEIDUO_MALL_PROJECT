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
        
        if(re.match(r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$', v_username)):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        user = authenticate(username=v_username,password=v_password)

        if(user == None):
            return JsonResponse({'code':400,'errmsg':'Incorrect Username/Password.'})

        login(request,user)

        if(v_remembered != None):
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        
        response = JsonResponse({'code':0,'errmsg':'OK'})
        response.set_cookie('username', v_username, path='/')
        return response

from django.contrib.auth import logout
class LogoutView(View):
    def delete(self, request):
        logout(request)
        response = JsonResponse({'code':0,'errmsg':'OK'})
        response.delete_cookie('username')
        return response

from utils.view import LoginRequiredJsonMixin
class CenterView(LoginRequiredJsonMixin, View):
    def get(self, request):
        # get request.user by using the middleware in setting
        info_data = {
            'username':request.user.username,
            'email':request.user.email,
            'mobile':request.user.mobile,
            'email_active':request.user.email_active
        }
        return JsonResponse({'code':0,'errmsg':'OK','info_data':info_data})

from django.conf import settings
from django.core.mail import send_mail
from apps.users.utils import generic_email_verify_token
from celery_tasks.email.tasks import celery_send_email
class EmailView(LoginRequiredJsonMixin, View):
    def put(self, request:HttpRequest):
        data = json.loads(request.body.decode())
        email = data.get('email')
        if(re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',email)):
            user = request.user
            user.email = email
            user.save() 
        else:
            return JsonResponse({'code':400,'errmsg':'Invalid Email Format.'})
        
        token = generic_email_verify_token(request.user.id)
        subject = 'Testing message from MEI_DUO MALL'
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s'%token
        message=''
        html_message = '<p>Dear User,</p>' \
               '<p>Thank you for using Meiduo Mall.</p>' \
               '<p>Your email address is: %s. Please click the link below to verify your email:</p>' \
               '<p><a href="%s">%s</a></p>' % (email, verify_url, verify_url)
        from_email = settings.EMAIL_FROM
        recipient_list = [email]
        celery_send_email.delay(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message)
        
        return JsonResponse({'code':0,'errmsg':'OK'})

from apps.users.utils import check_token
class EmailVerifyView(View):
    def put(self, request):
        data = request.GET
        token = data.get('token')
        if(token is None):
            return JsonResponse({'code':400, 'errmsg':'Incomplete data.'})
        user_id = check_token(token)
        if(user_id is None):
            return JsonResponse({'code':400, 'errmsg':'Incomplete data.'})
        user = User.objects.get(id=user_id)
        user.email_active = True
        user.save()
        return JsonResponse({'code':0, 'errmsg':'OK'})

from apps.users.models import Address

class AddressView(LoginRequiredJsonMixin, View):
    def get(self, request:HttpRequest):
        user = request.user
        addresses = Address.objects.filter(user=user, is_deleted=False)
        address_list = []
        for address in addresses:
            address_list.append( {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        return JsonResponse({'code':0,'errmsg':'OK','addresses':address_list})  

from apps.goods.models import SKU
from django_redis import get_redis_connection
class UserHistoryView(LoginRequiredJsonMixin, View):
    def post(self, request):
        user = request.user

        data = json.loads(request.body.decode())
        sku_id= data.get('sku_id')
        try:
            sku = SKU.objects.get(id = sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({'code':400,'errmsg':'No such item'})
        
        redis_cli = get_redis_connection('history')
        redis_cli.lrem(user.id, 0, sku_id)
        redis_cli.lpush(user.id,sku_id)
        redis_cli.ltrim(user.id, 0, 4)

        return JsonResponse({'code':0, 'errmsg':'ok'})

    def get(self,request):
        redis_cli = get_redis_connection('history')
        ids = redis_cli.lrange(request.user.id,0,4)
        history_list = []
        for sku_id in ids:
            try:
                sku_id = int(sku_id)
            except (TypeError, ValueError):
                continue

            try:
                sku = SKU.objects.get(id=sku_id)
            except SKU.DoesNotExist:
                continue

            history_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        return JsonResponse({'code':0, 'errmsg':'OK','skus':history_list})





class AddressCreateView(LoginRequiredJsonMixin, View):
    
    def post(self,request:HttpRequest):
        data = json.loads(request.body.decode())
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        user = request.user
        # verify data.
        address = Address.objects.create(
            user =user,
            title = receiver,
            receiver = receiver,
            province_id = province_id,
            city_id = city_id,
            district_id =district_id,
            place = place,
            mobile = mobile,
            tel = tel,
            email = email
        )
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return JsonResponse({'code':0,'errmsg':'OK','address':address_dict})