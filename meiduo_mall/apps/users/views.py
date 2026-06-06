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
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from apps.users.models import User
from django.http import HttpRequest, JsonResponse
import re
from utils.responses.general_response import JsonResponseCount, JsonResponseError, JsonResponsePass


class CSRFTokenView(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return JsonResponse({'code': 0, 'errmsg': 'OK'})


class UsernameCountView(View):

    """
    Verifies if the given username already exists in db.

    Args:
        request (HttpRequest): The received request.
        username (str): Given username from request url.
    Returns:
        JsonResponseCount:
            Look up in the db and return the # of identical username(s) in JsonResponse.
    Example:
        >>> get(request, 'Jone Doe')
        {'code': 0, 'count': 1, 'errmsg': 'ok'}
    """

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return JsonResponseCount(count)
    
class MobileView(View):

    """
    Verifies if the given phone number already exists in db.

    Args:
        request (HttpRequest): The received request.
        mobile (str): Given username from request url.
    Returns:
        JsonResponseCount:
            Look up in the db and return the # of identical phone number(s) in JsonResponse.
    Example:
        >>> get(request, '6464913294')
        {'code': 0, 'count': 1, 'errmsg': 'ok'}
    """

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponseCount(count)
    
import json
from django.contrib.auth import login,authenticate
import meiduo_mall.errors as error
class RegisterView(View):
    """
    Handle user registration requests.
    """

    def post(self, request: HttpRequest):
        """
        Register a new user.

        Args:
            request (HttpRequest):
                Incoming HTTP request containing user registration data.

        Returns:
            JsonResponse:
                Success response if registration succeeds,
                otherwise an error response.
        """

        req = request.body.decode()
        req_dict = json.loads(req)

        allow = req_dict['allow']
        mobile = req_dict['mobile']
        password = req_dict['password']
        password2 = req_dict['password2']
        username_req = req_dict['username']

        if not all([allow, mobile, password, password2, username_req]):
            return JsonResponseError(errmsg=error.INSUFFICIENT_DATA)

        if allow is not True:
            return JsonResponseError(
                errmsg=error.DISAGREE_TO_AGREEMENT
            )

        if not re.match(r'[a-zA-Z_-]{5,20}', username_req):
            return JsonResponseError(errmsg=error.BAD_USERNAME)

        if User.objects.filter(username=username_req).exists():
            return JsonResponseError(
                errmsg=error.DUPLICATE_USERNAME
            )

        if not re.match(
            r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$',
            mobile
        ):
            return JsonResponseError(
                errmsg=error.BAD_PHONE_NUM
            )

        if User.objects.filter(mobile=mobile).exists():
            return JsonResponseError(
                errmsg=error.DUPLICATE_PHONE_NUM
            )

        if not (8 <= len(password) <= 20):
            return JsonResponseError(
                errmsg=error.BAD_PASSWORD
            )

        if password != password2:
            return JsonResponseError(
                errmsg=error.MISMATCHED_PASSWORDS
            )

        from apps.verification.utils import verifyCaptcha

        captcha_result = verifyCaptcha(data=req_dict)
        if captcha_result['code'] != 0:
            return JsonResponseError(errmsg=captcha_result['errmsg'])

        # sms_code = req_dict.get('sms_code')
        # sms_result = verifySmsCode(mobile, sms_code)
        # if sms_result['code'] != 0:
        #     return JsonResponseError(errmsg=sms_result['errmsg'])

        user = User.objects.create_user(
            username=username_req,
            password=password,
            mobile=mobile
        )

        login(request, user)

        return JsonResponsePass()
    
class LoginView(View):
    def post(self,request:HttpRequest):
        data = json.loads(request.body.decode())
        v_username = data['username']
        v_password = data['password']
        v_remembered = data['remembered']

        if not all([v_username,v_password]):
            return JsonResponseError(errmsg=error.INSUFFICIENT_DATA)
        
        if(re.match(r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$', v_username)):
            user = User.objects.get(mobile=v_username)
        else:
            user = User.objects.get(username=v_username)
        user = authenticate(username=user.username,password=v_password)

        if(user == None):
            return JsonResponseError(errmsg=error.USER_DOES_NOT_EXIST)

        login(request,user)

        if v_remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        
        response = JsonResponse({'code':0,'errmsg':error.NO_ERROR})
        response.set_cookie('username', user.username, path='/')

        from apps.carts.utils import merge_cookie_to_redis
        response = merge_cookie_to_redis(request, response)
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
