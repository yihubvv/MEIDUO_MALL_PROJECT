import json

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

from django.utils import timezone
from apps.orders.models import OrderInfo
class OrderCommitView(LoginRequiredJsonMixin, View):
  def post(self, request:HttpRequest):
    user = request.user
    data = json.loads(request.body.decode())
    address_id = data.get('address_id')
    pay_method = data.get('pay_method')

    if not all([address_id, pay_method]):
      return JsonResponse({'code':400, 'errmsg':'bad input'})
    
    try:
      address = Address.objects.get(id = address_id)
    except Address.DoesNotExist:
      return JsonResponse({'code':400, 'errmsg':'bad input'})
    
    if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
      return JsonResponse({'code':400, 'errmsg':'bad input'})
    order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d'%user.id

    if pay_method == 1:
      pay_status = 2
    else:
      pay_status = 1

    total_count = 0
    from decimal import Decimal
    total_amount = Decimal('0')
    freight = Decimal('10.00')

    OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=total_count,
            total_amount=total_amount,
            freight=freight,
            pay_method=pay_method,
            status=pay_status
    )

