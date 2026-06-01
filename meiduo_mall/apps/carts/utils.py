import base64
import pickle
from django_redis import get_redis_connection
from django.http import HttpRequest, HttpResponse


def merge_cookie_to_redis(request:HttpRequest, response:HttpResponse):
    cookie_carts = request.COOKIES.get('carts')
    user = request.user
    if cookie_carts is not None:
      carts = pickle.loads(base64.b64decode(cookie_carts))
      cookie_dict = {}
      selected_ids = []
      unselected_ids = []

      for sku_id, count_selected_dict in carts.items():
        cookie_dict[sku_id] = count_selected_dict['count']
        if count_selected_dict['selected']:
          selected_ids.append(sku_id)
        else:
          unselected_ids.append(sku_id)
      redis_cli = get_redis_connection('carts')
      pipeline=redis_cli.pipeline()
      pipeline.hmset('carts_%s'%user.id, cookie_dict)
      if len(selected_ids)>0:
        pipeline.sadd('selected_%s'%user.id,*selected_ids)
      if len(unselected_ids)>0:
        pipeline.srem('unselected_%s'%user.id, *unselected_ids)
      pipeline.execute()
      response.delete_cookie('carts')
      return response