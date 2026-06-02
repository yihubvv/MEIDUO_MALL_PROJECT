import json
from decimal import Decimal
from time import sleep

from django.http import HttpRequest, JsonResponse
from django_redis import get_redis_connection
from django_redis.exceptions import ConnectionInterrupted
from redis.exceptions import RedisError
from django.views import View
from django.utils import timezone

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.view import LoginRequiredJsonMixin
from django.db import transaction

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
      'freight': freight,
      'default_address_id': user.default_address_id
    }

    return JsonResponse({'code':0, 'errmsg':'OK', 'context':context})


class OrderCommitView(LoginRequiredJsonMixin, View):
  def post(self, request:HttpRequest):
    user = request.user
    try:
      data = json.loads(request.body.decode())
    except (json.JSONDecodeError, UnicodeDecodeError):
      return JsonResponse({'code':400, 'errmsg':'bad input'})

    address_id = data.get('address_id')
    pay_method = data.get('pay_method')

    if not all([address_id, pay_method]):
      return JsonResponse({'code':400, 'errmsg':'bad input'})

    try:
      address_id = int(address_id)
      pay_method = int(pay_method)
    except (TypeError, ValueError):
      return JsonResponse({'code':400, 'errmsg':'bad input'})

    try:
      address = Address.objects.get(id=address_id, user=user, is_deleted=False)
    except Address.DoesNotExist:
      return JsonResponse({'code':400, 'errmsg':'bad input'})

    if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
      return JsonResponse({'code':400, 'errmsg':'bad input'})

    try:
      redis_cli = get_redis_connection('carts')
      pipeline = redis_cli.pipeline()
      pipeline.hgetall('carts_%s'%user.id)
      pipeline.smembers('selected_%s'%user.id)
      sku_id_counts, selected_ids = pipeline.execute()
    except (RedisError, ConnectionInterrupted):
      return JsonResponse({'code':500, 'errmsg':'cart service unavailable'})

    carts = {}
    for sku_id in selected_ids:
      count = sku_id_counts.get(sku_id)
      if count is None:
        continue
      try:
        carts[int(sku_id)] = int(count)
      except (TypeError, ValueError):
        continue

    if not carts:
      return JsonResponse({'code':400, 'errmsg':'Please select products first'})

    order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d'%user.id

    if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
      pay_status = OrderInfo.ORDER_STATUS_ENUM['UNSHIPPED']
    else:
      pay_status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

    total_count = 0
    total_amount = Decimal('0')
    freight = Decimal('10.00')

    try:
      with transaction.atomic():
        order_info = OrderInfo.objects.create(
          order_id=order_id,
          user=user,
          address=address,
          total_count=total_count,
          total_amount=total_amount,
          freight=freight,
          pay_method=pay_method,
          status=pay_status
        )

        for sku_id, count in carts.items():
          for i in range(10):
            try:
              sku = SKU.objects.get(id=sku_id)
            except SKU.DoesNotExist:
              transaction.set_rollback(True)
              return JsonResponse({'code':400,'errmsg':'Product not found'})

            if sku.stock < count:
              transaction.set_rollback(True)
              return JsonResponse({'code':400,'errmsg':'out of stock'})

            old_stock = sku.stock
            new_stock = sku.stock - count
            new_sales = sku.sales + count
            result = SKU.objects.filter(id=sku_id, stock=old_stock).update(stock=new_stock,sales=new_sales)
            if result == 0:
              sleep(0.05)
              continue

            total_count += count
            total_amount += count * sku.price
            OrderGoods.objects.create(
              order=order_info,
              sku=sku,
              count=count,
              price=sku.price
            )
            break
          else:
            transaction.set_rollback(True)
            return JsonResponse({'code':400,'errmsg':'failed'})

        order_info.total_count = total_count
        order_info.total_amount = total_amount
        order_info.save()
    except Exception:
      return JsonResponse({'code':500, 'errmsg':'submit order failed'})

    try:
      pipeline = redis_cli.pipeline()
      pipeline.hdel('carts_%s'%user.id, *selected_ids)
      pipeline.srem('selected_%s'%user.id, *selected_ids)
      pipeline.execute()
    except (RedisError, ConnectionInterrupted):
      pass

    return JsonResponse(
      {
        'code':0,
        'errmsg':'OK',
        'order_id':order_id
      }
      )
