from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from apps.verification.utils import verifyCaptcha

# Create your views here.
class ImageCodeView(View):
  def get(self, request, uuid):
    text,image=captcha.generate_captcha()
    redis_cli = get_redis_connection('code')
    redis_cli.setex(uuid,300,text)
  
    return HttpResponse(image, content_type='image/jpeg')
    
class SMSCodeView(View):
  def get(self, request, mobile):
    captcha_result = verifyCaptcha(request=request)
    if captcha_result['code'] != 0:
      return JsonResponse(captcha_result)

    redis_cli = get_redis_connection('code')
    
    send_flag=redis_cli.get('send_flag_%s'%mobile)
    if send_flag is not None:
      return JsonResponse({'code':400,'errmsg':'SMS sent repeatedly.'})
    from random import randint
    sms_code = '%06d'%randint(0,999999)

# higher performance.
    pipeline = redis_cli.pipeline()

    pipeline.setex(mobile,300,sms_code)
    pipeline.setex('send_flag_%s'%mobile,60,1)

    pipeline.execute()
    
    # from libs.yuntongxun.sms import CCP
    # CCP().send_template_sms(mobile,[sms_code,5],1)
    from celery_tasks.sms.tasks import celery_send_sms_code
    
    celery_send_sms_code.delay(mobile, sms_code)

    return JsonResponse({'code':0, 'errmsg':"OK"})
    
