from django.db import models

# Create your models here.
from apps.orders.models import OrderInfo
from utils.models import BaseModel

class Payment(BaseModel):
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name='order')
    trade_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='order_id')

    class Meta:
        db_table = 'tb_payment'
        verbose_name = 'payment_info'
        verbose_name_plural = verbose_name