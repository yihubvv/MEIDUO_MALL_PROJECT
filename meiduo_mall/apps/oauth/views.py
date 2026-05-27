from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall import settings
from apps.oauth.models import OAuthQQUser
# Create your views here.
class QQLoginURLView(View):
  def get(self,request:HttpRequest):
    qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                 client_secret=settings.QQ_CLIENT_SECRET,
                 redirect_uri=settings.QQ_REDIRECT_URI,
                 state='XXXXX') 
    qq_login_url = qq.get_qq_url()
    return JsonResponse({'code':0,'errmsg':'OK','login_url':qq_login_url})

from django.contrib.auth import login
import json
import re
from apps.users.models import User

class OauthQQView(View):
  def get(self, request:HttpRequest):
    code = request.GET.get('code')
    if code is None:
      return JsonResponse({'code':400,'errmsg':'Invalid Code.'})
    qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                 client_secret=settings.QQ_CLIENT_SECRET,
                 redirect_uri=settings.QQ_REDIRECT_URI,
                 state='XXXXX')
    token = qq.get_access_token(code)
    openid=qq.get_open_id(token)

    try:
      qquser=OAuthQQUser.objects.get(openid=openid)
    except OAuthQQUser.DoesNotExist:
      response = JsonResponse({'code':400,'access_token':openid})
      return response
    else:
      login(request,qquser.user)
      response = JsonResponse({'code':0, 'errmsg':'OK'})
      response.set_cookie('username',qquser.user.username)
      return response

  def post(self, request:HttpRequest):
    data = json.loads(request.body.decode())
    v_mobile=data.get('mobile')
    vpassword=data.get('password')
    v_sms_code=data.get('sms_code')
    v_open_id=data.get('access_token')

    if not all([v_mobile, vpassword, v_sms_code]):
        return JsonResponse({'code': 400, 'errmsg': 'Incomplete data.'})
    
    if not re.match(r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$', v_mobile):
        return JsonResponse({'code': 400,'errmsg': 'Invalid Phone Number.'})

    if not re.match(r'^[0-9A-Za-z]{8,20}$', vpassword):
        return JsonResponse({'code': 400,'errmsg': 'Password should be 8-20 characters.'})

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
        return JsonResponse({'code':400,'errmsg':'wrong password.'})
      
    OAuthQQUser.objects.create(user=user,openid=v_open_id)

    login(request,user)
    response = JsonResponse({'code':0,'errmsg':'OK'})
    response.set_cookie('username',user.username)
    return response
