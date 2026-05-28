from django.db import models

# Create your models here.

# 1. Define our own model
# We need to encrypt passwords and also validate passwords during login
# class User(models.Model):
#     username=models.CharField(max_length=20,unique=True)
#     password=models.CharField(max_length=20)
#     mobile=models.CharField(max_length=11,unique=True)

# 2. Django comes with a built-in user model
# This user model already includes password encryption and password validation
# from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser

# use the user model provided by the system, add info like mobile for the actual needs.
class User(AbstractUser):
    mobile=models.CharField(max_length=11,unique=True)
    email_active = models.BooleanField(default=False, verbose_name='Verify Email Status')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Default Address')

    class Meta:
        db_table='tb_users'
        verbose_name='User Management'
        verbose_name_plural=verbose_name


from utils.models import BaseModel
class Address(BaseModel):
    """User Address"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='User')
    title = models.CharField(max_length=20, verbose_name='Address Name')
    receiver = models.CharField(max_length=20, verbose_name='Recipient')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='Province')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='City')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='District')
    place = models.CharField(max_length=50, verbose_name='Address')
    mobile = models.CharField(max_length=11, verbose_name='Mobile Phone')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='Landline Phone')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='Email')
    is_deleted = models.BooleanField(default=False, verbose_name='Logical Deletion')

    class Meta:
        db_table = 'tb_address'
        verbose_name = 'User Address'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']