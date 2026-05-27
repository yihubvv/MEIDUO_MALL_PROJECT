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

  