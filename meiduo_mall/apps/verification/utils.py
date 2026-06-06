import json

from django.http import HttpRequest
from django_redis import get_redis_connection
import meiduo_mall.errors as error

def get_request_data(request: HttpRequest):
    if request.method == 'GET':
        return request.GET

    try:
        return json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return {}


def verifyCaptcha(request: HttpRequest = None, data=None):
    data = data or get_request_data(request)
    image_code = data.get('image_code')
    uuid = data.get('image_code_id')

    if not all([image_code, uuid]):
        return {'code': 400, 'errmsg': error.INSUFFICIENT_DATA}

    redis_cli = get_redis_connection('code')

    if redis_image_code is None:
        return {'code': 400, 'errmsg': error.Captcha_EXPIRED}
    
    redis_image_code = redis_cli.get(uuid)
    redis_cli.delete(uuid)

    if redis_image_code.decode().lower() != image_code.lower():
        return {'code': 400, 'errmsg': error.Captcha_MISMATCHED}
    return {'code': 0, 'errmsg': error.NO_ERROR}


def verifySmsCode(mobile, sms_code):
    if not all([mobile, sms_code]):
        return {'code': 400, 'errmsg': 'Incomplete SMS code data.'}

    redis_cli = get_redis_connection('code')
    redis_sms_code = redis_cli.get(mobile)

    if redis_sms_code is None:
        return {'code': 400, 'errmsg': 'SMS code expired.'}

    if redis_sms_code.decode() != sms_code:
        return {'code': 400, 'errmsg': 'SMS code mismatched.'}

    return {'code': 0, 'errmsg': 'OK'}
