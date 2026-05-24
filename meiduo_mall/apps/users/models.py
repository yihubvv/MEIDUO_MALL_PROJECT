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

    class Meta:
        db_table='tb_users'
        verbose_name='User Management'
        verbose_name_plural=verbose_name