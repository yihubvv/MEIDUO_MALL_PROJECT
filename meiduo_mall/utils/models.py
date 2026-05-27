from django.db import models


class BaseModel(models.Model):

    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Of Creation"
    )

    update_time = models.DateTimeField(
        auto_now=True,
        verbose_name="Date Of Update"
    )

    class Meta:
        abstract = True