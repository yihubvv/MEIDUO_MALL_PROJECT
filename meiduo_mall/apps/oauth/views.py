from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, JsonResponse
from QQLoginTool.QQtool import OAuthQQ
from meiduo_mall import settings
# Create your views here.
class QQLoginURLView(View):
  def get(self,request:HttpRequest):
    qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                 client_secret=settings.QQ_CLIENT_SECRET,
                 redirect_uri=settings.QQ_REDIRECT_URI,
                 state='XXXXX')
    qq_login_url = qq.get_qq_url()
    return JsonResponse({'code':0,'errmsg':'OK','login_url':qq_login_url})

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
    pass

  