from django.db import models

# Create your models here.
from utils.models import BaseModel

class GoodsCategory(BaseModel):
    name = models.CharField(max_length=10, verbose_name='name')
    parent = models.ForeignKey('self', related_name='subs', null=True, blank=True, on_delete=models.CASCADE, verbose_name='parent')

    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = 'goods_category'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsChannelGroup(BaseModel):
    name = models.CharField(max_length=20, verbose_name='GoodsChannel')

    class Meta:
        db_table = 'tb_channel_group'
        verbose_name = 'GoodsChannel'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsChannel(BaseModel):
    group = models.ForeignKey(GoodsChannelGroup, on_delete=models.CASCADE, verbose_name='GoodsChannel Name')
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='GoodsChannel Type')
    url = models.CharField(max_length=50, verbose_name='link')
    sequence = models.IntegerField(verbose_name='order')

    class Meta:
        db_table = 'tb_goods_channel'
        verbose_name = 'GoodsChannel'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name


class Brand(BaseModel):
    name = models.CharField(max_length=20, verbose_name='Name')
    logo = models.ImageField(verbose_name='Logo')
    first_letter = models.CharField(max_length=1, verbose_name='Initial')

    class Meta:
        db_table = 'tb_brand'
        verbose_name = 'Brand'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SPU(BaseModel):
    """SPU"""
    name = models.CharField(max_length=50, verbose_name='Name')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name='Brand')
    category1 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat1_spu', verbose_name='First Class')
    category2 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat2_spu', verbose_name='Second Class')
    category3 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat3_spu', verbose_name='Third Class')
    sales = models.IntegerField(default=0, verbose_name='Sales')
    comments = models.IntegerField(default=0, verbose_name='Comments')
    desc_detail = models.TextField(default='', verbose_name='Intro')
    desc_pack = models.TextField(default='', verbose_name='Info')
    desc_service = models.TextField(default='', verbose_name='Aftersale')

    class Meta:
        db_table = 'tb_spu'
        verbose_name = 'SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SKU(BaseModel):
    name = models.CharField(max_length=50, verbose_name='Name')
    caption = models.CharField(max_length=100, verbose_name='Subtitle')
    spu = models.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='Product')
    category = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, verbose_name='Category')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Unit Price')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Cost Price')
    market_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Market Price')
    stock = models.IntegerField(default=0, verbose_name='Stock')
    sales = models.IntegerField(default=0, verbose_name='Sales Volume')
    comments = models.IntegerField(default=0, verbose_name='Number of Reviews')
    is_launched = models.BooleanField(default=True, verbose_name='Available for Sale')
    default_image = models.ImageField(
        max_length=200,
        default='',
        null=True,
        blank=True,
        verbose_name='Default Image'
    )
    class Meta:
        db_table = 'tb_sku'
        verbose_name = 'SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.id, self.name)


class SKUImage(BaseModel):
    """SKU Image"""
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='SKU')
    image = models.ImageField(verbose_name='Image')

    class Meta:
        db_table = 'tb_sku_image'
        verbose_name = 'SKU Image'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.sku.name, self.id)


class SPUSpecification(BaseModel):
    """SPU Specification"""
    spu = models.ForeignKey(
        SPU,
        on_delete=models.CASCADE,
        related_name='specs',
        verbose_name='SPU'
    )
    name = models.CharField(max_length=20, verbose_name='Specification Name')

    class Meta:
        db_table = 'tb_spu_specification'
        verbose_name = 'SPU Specification'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.spu.name, self.name)


class SpecificationOption(BaseModel):
    """Specification Option"""
    spec = models.ForeignKey(
        SPUSpecification,
        related_name='options',
        on_delete=models.CASCADE,
        verbose_name='Specification'
    )
    value = models.CharField(max_length=20, verbose_name='Option Value')

    class Meta:
        db_table = 'tb_specification_option'
        verbose_name = 'Specification Option'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.spec, self.value)


class SKUSpecification(BaseModel):
    """SKU Specification"""
    sku = models.ForeignKey(
        SKU,
        related_name='specs',
        on_delete=models.CASCADE,
        verbose_name='SKU'
    )
    spec = models.ForeignKey(
        SPUSpecification,
        on_delete=models.PROTECT,
        verbose_name='Specification Name'
    )
    option = models.ForeignKey(
        SpecificationOption,
        on_delete=models.PROTECT,
        verbose_name='Specification Value'
    )

    class Meta:
        db_table = 'tb_sku_specification'
        verbose_name = 'SKU Specification'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s - %s' % (
            self.sku,
            self.spec.name,
            self.option.value
        )