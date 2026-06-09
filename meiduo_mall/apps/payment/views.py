from django.shortcuts import render
from utils.responses.general_response import JsonResponseCount, JsonResponseError, JsonResponsePass
import meiduo_mall.errors as error
from django.http import HttpResponseBadRequest,JsonResponse
import meiduo_mall.settings as settings
from utils.view import LoginRequiredJsonMixin
from django.views import View
from apps.orders.models import OrderInfo
from alipay import AliPay
# Create your views here.
class PaymentView(LoginRequiredJsonMixin, View):

    def get(self,request, order_id):
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return HttpResponseBadRequest(error.INSUFFICIENT_DATA)

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=True
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="MeiDuo%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )

        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return JsonResponse({'code': 0, 'errmsg': error.NO_ERROR, 'alipay_url': alipay_url})