from itertools import count

from django.contrib.auth import get_user_model
from django.db import models
from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    image = models.ImageField(upload_to='recipes/')
    cooking_time = models.SmallIntegerField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag, through='TagRecipe', related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe', related_name='recipes'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Связь тэг-рецепт'
        verbose_name_plural = 'Связи тэг-рецепт'

    def __str__(self):
        return f'{self.tag} - {self.recipe}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()

    class Meta:
        verbose_name = 'Связь ингредиент-рецепт'
        verbose_name_plural = 'Связи ингредиент-рецепт'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} ({self.quantity})'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shoping_cart'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shoping_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранное'

    def __str__(self):
        return f'{self.user} {self.recipe}'
