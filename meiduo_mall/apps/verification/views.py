from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

# Create your views here.
class ImageCodeView(View):
  def get(self, request, uuid):
    text,image=captcha.generate_captcha()
    redis_cli = get_redis_connection('code')
    redis_cli.setex(uuid,100,text)
  
    return HttpResponse(image, content_type='image/jpeg')
    
class SMSCodeView(View):
  def get(self, request, mobile):
    image_code = request.GET.get('image_code')
    uuid = request.get('image_code_id')
    if not all([image_code,uuid]):
      return JsonResponse({'code':400,'errmsg':'incomplete input'})
    redis_cli = get_redis_connection('code')
    redis_image_code=redis_cli.get(uuid)
    if(redis_image_code is None):
      return JsonResponse({'code':400,'errmsg':'SMS code expired'})
    if(redis_image_code.decode().lower() != image_code.lower()):
      return JsonResponse({'code':400,'errmsg':'Code mismatched'})
    
    from random import randint
    sms_code = '%06d'%randint(0,999999)
    redis_cli.setex(mobile,300,sms_code)
    
    from libs.yuntongxun.sms import CCP
    CCP().send_template_sms(mobile,[sms_code,5],1)
    
    return JsonResponse({'code':0, 'errmsg':"OK"})
    

