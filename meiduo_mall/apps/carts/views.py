from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, JsonResponse, HttpResponse
# Create your views here.
import utils.responses.general_response as res

import json
from apps.goods.models import SKU
from django_redis import get_redis_connection
import pickle
import base64
import meiduo_mall.errors as error
class CartsView(View):
  @staticmethod
  def _normalize_carts(carts):
    """
    Organizes cart data.
    Args:
        cart:
            everything inside cart.

    Returns:
        normalized_carts:
          organized cart.
    """

    normalized_carts = {}
    for sku_id, cart in carts.items():
      try:
        sku_id = int(sku_id)
        count = int(cart.get('count', 0))
      except (TypeError, ValueError):
        continue

      normalized_carts[sku_id] = {
        'count': count,
        'selected': bool(cart.get('selected', False))
      }
    return normalized_carts

  def get(self, request:HttpRequest):
    """
    Gets cart info.
    Args:
        request:
            request from frontend.

    Returns:
        Json response:
          JsonResponse with organized cart data.
    """

    user = request.user
    if user.is_authenticated:
      redis_cli = get_redis_connection('carts')
      sku_id_counts = redis_cli.hgetall('carts_%s'%user.id)
      selected_ids = redis_cli.smembers('selected_%s'%user.id)
      selected_ids = {int(sku_id) for sku_id in selected_ids}
      carts = {}
      for sku_id, count in sku_id_counts.items():
        sku_id = int(sku_id)
        carts[sku_id] = {
          'count':int(count),
          'selected': sku_id in selected_ids
        }

    else:
      cookie_carts = request.COOKIES.get('carts')
      if cookie_carts is not None:
        carts  = pickle.loads(base64.b64decode(cookie_carts))
      else: 
        carts = {}
      carts = self._normalize_carts(carts)
    sku_ids = carts.keys()
    skus= SKU.objects.filter(id__in=sku_ids)
    sku_list = []
    for sku in skus:
      sku_list.append({
        'id':sku.id,
        'price':sku.price,
        'name':sku.name,
        'default_image_url':sku.default_image.url,
        'selected':carts[sku.id]['selected'],
        'count':carts[sku.id]['count'],
        'amount':sku.price * carts[sku.id]['count']
      })
    return JsonResponse({'code':0, 'errmsg':error.NO_ERROR,'cart_skus':sku_list})
  
  def post(self, request:HttpRequest):
    """
    Allows user to add items to their carts.
    Args:
        request:
            request from frontend.

    Returns:
        Json response:
          JsonResponse with OK on success.
    """
    data = json.loads(request.body.decode())
    sku_id = data.get('sku_id')
    count = data.get('count')

    try:
      SKU.objects.get(id=sku_id)
    except SKU.DoesNotExist:
      return res.JsonResponseError(errmsg=error.DOES_NOT_EXIST)
    
    try:
      count = int(count)
    except Exception:
      count = 1

    user = request.user
    if user.is_authenticated:
      redis_cli = get_redis_connection('carts')
      redis_cli.hincrby('carts_%s'%user.id, sku_id, count)
      redis_cli.sadd('selected_%s'%user.id, sku_id)
      return res.JsonResponsePass(errmsg=error.NO_ERROR)
    else:
      cookie_carts = request.COOKIES.get('carts')
      if cookie_carts:
        carts = pickle.loads(base64.b64decode(cookie_carts))
      else:
        carts = {}
      carts = self._normalize_carts(carts)
      sku_id = int(sku_id)
      if sku_id in carts:
        orign_count = carts[sku_id]['count']
        count += orign_count

      carts[sku_id] = {
        'count':int(count),
        'selected':True
      }
      carts_bytes = pickle.dumps(carts)
      base64encode = base64.b64encode(carts_bytes)
      response = JsonResponse({'code':0, 'errmsg':error.NO_ERROR})
      response.set_cookie('carts',base64encode.decode(), max_age=3600*24*7)
      return response

  def put(self,request:HttpRequest):
    """
    Allows user to add/substract items in their cart.
    Args:
        request:
            request from frontend.

    Returns:
        Json response:
          JsonResponse with OK on success,400 on failure.
    """
    user = request.user
    data = json.loads(request.body.decode())
    sku_id = data.get('sku_id')
    count = data.get('count')
    selected = data.get('selected')

    if not all([sku_id, count]):
      return res.JsonResponseError(errmsg=error.INSUFFICIENT_DATA)
    try:
      SKU.objects.get(id=sku_id)
    except SKU.DoesNotExist:
      return res.JsonResponseError(errmsg=error.INSUFFICIENT_DATA)
    try:
      count = int(count)
    except Exception:
      count = 1
    
    if user.is_authenticated:
      redis_cli = get_redis_connection('carts')
      pipeline = redis_cli.pipeline()
      pipeline.hset('carts_%s'%user.id,sku_id,count)
      if(selected):
        pipeline.sadd('selected_%s'%user.id, sku_id)
      else:
        pipeline.srem('selected_%s'%user.id, sku_id)
      pipeline.execute()
      return JsonResponse({'code':0, 'errmsg':error.NO_ERROR, 'cart_sku':{'count':count, 'selected':selected}})
    else:
      cookie_cart = request.COOKIES.get('carts')
      if cookie_cart is not None:
        carts = pickle.loads(base64.b64decode(cookie_cart))

      else:
        carts = {}
      carts = self._normalize_carts(carts)
      sku_id = int(sku_id)

      if sku_id in carts:
        carts[sku_id] = {
          'count':count,
          'selected':selected
        }
      
      new_carts = base64.b64encode(pickle.dumps(carts))
      response = JsonResponse({'code':0, 'errmsg':error.NO_ERROR, 'cart_sku':{'count':count, 'selected':selected}})
      response.set_cookie('carts', new_carts.decode(), max_age=3600*24*7)
      return response

  def delete(self, request:HttpRequest):
    """
    Allows user to delete items in their cart.
    Args:
        request:
            request from frontend.

    Returns:
        Json response:
          JsonResponse with OK on success,400 on failure.
    """
    data = json.loads(request.body.decode())
    sku_id = data.get('sku_id')
    try:
      SKU.objects.get(pk=sku_id)
    except SKU.DoesNotExist:
      return res.JsonResponseError(errmsg=error.DOES_NOT_EXIST)
    user = request.user
    if user.is_authenticated:
      redis_cli = get_redis_connection('carts')
      redis_cli.hdel('carts_%s'%user.id, sku_id)
      redis_cli.srem('selected_%s'%user.id, sku_id)
      return res.JsonResponsePass(errmsg=error.NO_ERROR)
    else:
      cookie_cart = request.COOKIES.get('carts')
      if(cookie_cart is not None):
        carts = pickle.loads(base64.b64decode(cookie_cart))

      else:
        carts = {}
      carts = self._normalize_carts(carts)
      sku_id = int(sku_id)
      if sku_id in carts:
        del carts[sku_id]
      new_carts = base64.b64encode(pickle.dumps(carts))
      response = JsonResponse({'code':0, 'errmsg':error.NO_ERROR})
      response.set_cookie('carts', new_carts.decode(), max_age=7*3600*24)
      return response


class CartsSelectAllView(View):
  """
  Allows user to select all items in their cart.
  Args:
      request:
          request from frontend.
  Returns:
      Json response:
        JsonResponse with OK on success,400 on failure.
  """
  def put(self, request:HttpRequest):
    data = json.loads(request.body.decode())
    selected = data.get('selected')
    user = request.user

    if user.is_authenticated:
      redis_cli = get_redis_connection('carts')
      sku_ids = redis_cli.hkeys('carts_%s'%user.id)
      if sku_ids:
        if selected:
          redis_cli.sadd('selected_%s'%user.id, *sku_ids)
        else:
          redis_cli.srem('selected_%s'%user.id, *sku_ids)
      return JsonResponse({'code':0, 'errmsg':error.NO_ERROR,'selected':selected})

    cookie_cart = request.COOKIES.get('carts')
    if cookie_cart is not None:
      carts = pickle.loads(base64.b64decode(cookie_cart))
    else:
      carts = {}
    carts = CartsView._normalize_carts(carts)

    for sku_id in carts:
      carts[sku_id]['selected'] = selected

    response = JsonResponse({'code':0, 'errmsg':error.NO_ERROR, 'selected':selected})
    response.set_cookie(
      'carts',
      base64.b64encode(pickle.dumps(carts)).decode(),
      max_age=7*3600*24
    )
    return response

class CartsSimpleView(View):

    def get(self, request):
        user = request.user
        if user.is_authenticated:
          redis_cli = get_redis_connection('carts')
          sku_id_counts = redis_cli.hgetall('carts_%s'%user.id)
          selected_ids = redis_cli.smembers('selected_%s'%user.id)
          selected_ids = {int(sku_id) for sku_id in selected_ids}
          carts = {}
          for sku_id, count in sku_id_counts.items():
            sku_id = int(sku_id)
            carts[sku_id] = {
              'count':int(count),
              'selected': sku_id in selected_ids
            }

        else:
          cookie_carts = request.COOKIES.get('carts')
          if cookie_carts is not None:
            carts  = pickle.loads(base64.b64decode(cookie_carts))
          else: 
            carts = {}
          carts = CartsView._normalize_carts(carts)
        sku_ids = carts.keys()
        skus= SKU.objects.filter(id__in=sku_ids)
        sku_list = []
        for sku in skus:
          sku_list.append({
            'id':sku.id,
            'name':sku.name,
            'default_image_url':sku.default_image.url,
            'count':carts[sku.id]['count'],
          })
        return JsonResponse({'code':0, 'errmsg':error.NO_ERROR, 'cart_skus':sku_list})
