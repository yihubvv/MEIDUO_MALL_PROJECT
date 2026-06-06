from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall import settings
from apps.oauth.models import OAuthQQUser
import meiduo_mall.errors as error
# Create your views here.
class QQLoginURLView(View):
  def get(self,request:HttpRequest):
    """
    Send oauth request to QQ side.
    Args:
        request (HttpRequest):
            Incoming HTTP request containing QQ data
    Returns:
        info_data:
            Redirects to QQ login URL.
    """
    qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                 client_secret=settings.QQ_CLIENT_SECRET,
                 redirect_uri=settings.QQ_REDIRECT_URI,
                 state='XXXXX') 
    qq_login_url = qq.get_qq_url()
    return JsonResponse({'code':0,'errmsg':error.NO_ERROR,'login_url':qq_login_url})

from django.contrib.auth import login
import json
import re
from apps.users.models import User
from apps.oauth.utils import generic_open_id, decode_open_id
from utils.responses import general_response
class OauthQQView(View):
  def get(self, request:HttpRequest):
    """
    Request openid and verifies if user has logged in with QQ before.
    Args:
        request:
            request from frontend.
    Returns:
        response:
          response contains username as cookie or access token to prompt the user to bind their account.
    """
    code = request.GET.get('code')
    if code is None:
      return JsonResponse({'code':400,'errmsg':error.BAD_CODE})
    qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                 client_secret=settings.QQ_CLIENT_SECRET,
                 redirect_uri=settings.QQ_REDIRECT_URI,
                 state='XXXXX')
    token = qq.get_access_token(code)

    openid = qq.get_open_id(token)

    qquser = OAuthQQUser.objects.get(openid=openid)
    if qquser is None:
      response = JsonResponse({'code':400,'access_token':generic_open_id(openid)})
      return response

    login(request,qquser.user)
    response = JsonResponse({'code':0,'errmsg':error.NO_ERROR})
    response.set_cookie('username',qquser.user.username)
    return response

  def post(self, request:HttpRequest):
    """
    Bind user info with QQ account.
    Args:
        request:
            request from frontend.
    Returns:
        response:
          response with an error message or success.
    """
    data = json.loads(request.body.decode())
    v_mobile=data.get('mobile')
    vpassword=data.get('password')
    v_sms_code=data.get('sms_code')
    v_open_id=data.get('access_token')

    v_open_id = decode_open_id(v_open_id)

    if(v_open_id is None):
      return JsonResponse({'code': 400,'errmsg': error.BAD_CODE})
    
    if not all([v_mobile, vpassword, v_sms_code]):
        return JsonResponse({'code': 400, 'errmsg': error.INSUFFICIENT_DATA})
    
    if not re.match(r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$', v_mobile):
        return JsonResponse({'code': 400,'errmsg': error.BAD_PHONE_NUM})

    if not re.match(r'^[0-9A-Za-z]{8,20}$', vpassword):
        return JsonResponse({'code': 400,'errmsg': error.BAD_PASSWORD})

    # verify sms code.
    # redis_conn = get_redis_connection('code')

    # sms_code_server = redis_conn.get('sms_%s' % mobile)

    # if sms_code_server is None:

    # return JsonResponse({
    #     'code': 400,
    #     'errmsg': 'bad sms'
    # })

    # if v_sms_code != sms_code_server.decode():
    
    #     return JsonResponse({
    #         'code': 400,
    #         'errmsg': 'bad code'
    #     })
    try:
      user = User.objects.get(mobile=v_mobile)
    except User.DoesNotExist:
      user=User.objects.create_user(username=v_mobile,mobile=v_mobile,password=vpassword)
    else:
      if not (user.check_password(vpassword)):
        return general_response.JsonResponseError(errmsg=error.BAD_PASSWORD)
      
    qquser = OAuthQQUser.objects.get(openid=v_open_id)
    if qquser is not None:
      login(request, qquser.user)
      response = JsonResponse({'code':0,'errmsg':error.NO_ERROR})
      response.set_cookie('username',qquser.user.username)
      return response

    OAuthQQUser.objects.create(user=user,openid=v_open_id)

    login(request,user)
    response = JsonResponse({'code':0,'errmsg':error.NO_ERROR})
    response.set_cookie('username',user.username)
    return response
