from django.db import models
from apps.goods.models import SKU
from apps.users.models import User, Address
from utils.models import BaseModel


class OrderInfo(BaseModel):
    """Order Information"""

    PAY_METHODS_ENUM = {
        "CASH": 1,
        "ALIPAY": 2
    }

    PAY_METHOD_CHOICES = (
        (1, "Cash on Delivery"),
        (2, "Alipay"),
    )

    ORDER_STATUS_ENUM = {
        "UNPAID": 1,
        "UNSHIPPED": 2,
        "UNRECEIVED": 3,
        "UNCOMMENTED": 4,
        "FINISHED": 5
    }

    ORDER_STATUS_CHOICES = (
        (1, "Pending Payment"),
        (2, "Pending Shipment"),
        (3, "Pending Receipt"),
        (4, "Pending Review"),
        (5, "Completed"),
        (6, "Cancelled"),
    )

    order_id = models.CharField(
        max_length=64,
        primary_key=True,
        verbose_name="Order ID"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Customer"
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        verbose_name="Shipping Address"
    )

    total_count = models.IntegerField(
        default=1,
        verbose_name="Total Quantity"
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Amount"
    )

    freight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Shipping Fee"
    )

    pay_method = models.SmallIntegerField(
        choices=PAY_METHOD_CHOICES,
        default=1,
        verbose_name="Payment Method"
    )

    status = models.SmallIntegerField(
        choices=ORDER_STATUS_CHOICES,
        default=1,
        verbose_name="Order Status"
    )

    class Meta:
        db_table = "tb_order_info"
        verbose_name = "Order Information"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_id


class OrderGoods(BaseModel):
    """Order Item"""

    SCORE_CHOICES = (
        (0, "0 Points"),
        (1, "20 Points"),
        (2, "40 Points"),
        (3, "60 Points"),
        (4, "80 Points"),
        (5, "100 Points"),
    )

    order = models.ForeignKey(
        OrderInfo,
        related_name='skus',
        on_delete=models.CASCADE,
        verbose_name="Order"
    )

    sku = models.ForeignKey(
        SKU,
        on_delete=models.PROTECT,
        verbose_name="Product"
    )

    count = models.IntegerField(
        default=1,
        verbose_name="Quantity"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Unit Price"
    )

    comment = models.TextField(
        default="",
        verbose_name="Review"
    )

    score = models.SmallIntegerField(
        choices=SCORE_CHOICES,
        default=5,
        verbose_name="Satisfaction Score"
    )

    is_anonymous = models.BooleanField(
        default=False,
        verbose_name="Anonymous Review"
    )

    is_commented = models.BooleanField(
        default=False,
        verbose_name="Reviewed"
    )

    class Meta:
        db_table = "tb_order_goods"
        verbose_name = "Order Item"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name