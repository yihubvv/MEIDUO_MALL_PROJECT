from django.db import models

# Create your models here.

class Area(models.Model):
    """Administrative Region"""
    name = models.CharField(max_length=20, verbose_name='Name')

    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='subs',
        null=True,
        blank=True,
        verbose_name='Parent Administrative Region'
    )

    class Meta:
        db_table = 'tb_areas'
        verbose_name = 'Province / City / District'
        verbose_name_plural = 'Province / City / District'

    def __str__(self):
        return self.name