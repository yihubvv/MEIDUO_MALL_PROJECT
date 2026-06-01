from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views import View
from utils.view import LoginRequiredJsonMixin
from apps.users.models import Address
from django_redis import get_redis_connection
from apps.goods.models import SKU
# Create your views here.
class OrderSettlementView(LoginRequiredJsonMixin, View):
  def get(self, request:HttpRequest):
    user = request.user
    addresses = Address.objects.filter(user=user, is_deleted=False)
    address_list = []

    for address in addresses:
      address_list.append({
      'id': address.id,
      'province': address.province.name,
      'city': address.city.name,
      'district': address.district.name,
      'place': address.place,
      'receiver': address.receiver,
      'mobile': address.mobile
      })
    
    redis_cli = get_redis_connection('carts')
    pipeline = redis_cli.pipeline()
    pipeline.hgetall('carts_%s'%user.id)
    pipeline.smembers('selected_%s'%user.id)
    result = pipeline.execute()
    sku_id_counts = result[0]
    selected_ids = result[1]
    selected_carts = {}
    for sku_id in selected_ids:
      count = sku_id_counts.get(sku_id)
      if count is None:
        continue
      selected_carts[int(sku_id)] = int(count)
    sku_list = []
    skus = SKU.objects.filter(id__in=selected_carts.keys())
    for sku in skus:
      sku_list.append({
        'id':sku.id,
        'name':sku.name,
        'count':selected_carts[sku.id],
        'default_image_url': sku.default_image.url if sku.default_image else '',
        'price': sku.price
      })
    from decimal import Decimal
    freight = Decimal('10')

    context = {
      'skus': sku_list,
      'addresses': address_list,
      'freight': freight
    }

    return JsonResponse({'code':0, 'errmsg':'OK', 'context':context})
