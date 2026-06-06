import json

from django.http import HttpRequest
from django_redis import get_redis_connection
import meiduo_mall.errors as error

def get_request_data(request: HttpRequest):
    """
      Get data from request from either GET or body.
      Args:
          request (HttpRequest):
            Incoming HTTP request containing user data.
      Returns:
          Json string data or GET data.
    """
    if request.method == 'GET':
        return request.GET

    try:
        return json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return {}


def verifyCaptcha(request: HttpRequest = None, data=None):
    """
      Verifies if user input is correct and delete current captcha afterwards.
      Args:
          request (HttpRequest):
            Incoming HTTP request containing user data.
          data:
            Frontend data contains image code from user.
      Returns:
          HttpResponse:
              Returns ok on success, error message otherwise.
    """
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

import utils.responses.general_response as general_response
import meiduo_mall.errors as error
def verifySmsCode(mobile, sms_code):
    """
      Verifies if an user input sms code is correct.
      Args:
          mobile:
            Users' phone numbers.
          sms_code:
            The sms_code from users.
      Returns:
          HttpResponse:
              Returns ok on success, error message otherwise.
    """
    if not all([mobile, sms_code]):
        return general_response.JsonResponseError(errmsg=error.INSUFFICIENT_DATA)

    redis_cli = get_redis_connection('code')
    redis_sms_code = redis_cli.get(mobile)

    if redis_sms_code is None:
        return general_response.JsonResponseError(errmsg=error.SMS_EXPIRED)

    if redis_sms_code.decode() != sms_code:
        return general_response.JsonResponseError(errmsg=error.SMS_MISMATCHED)

    return general_response.JsonResponsePass(errmsg=error.NO_ERROR)
