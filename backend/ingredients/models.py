from django.db import models
from django.db.models.constraints import UniqueConstraint


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиет'
        verbose_name_plural = 'Ингридиенты'
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name
