from django.db import models
from django.core.validators import MinLengthValidator


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(
        max_length=7,
        unique=True,
        validators=(MinLengthValidator(7),)
    )
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name
