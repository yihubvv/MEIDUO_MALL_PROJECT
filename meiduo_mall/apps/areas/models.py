from django.db import models


class Area(models.Model):
    """Province / city / district administrative region."""

    name = models.CharField(max_length=20, verbose_name='Name')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subs',
        verbose_name='Parent Administrative Region',
    )

    class Meta:
        db_table = 'tb_areas'
        verbose_name = 'Province / City / District'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
