from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    image = models.ImageField(upload_to='recipes/')
    cooking_time = models.SmallIntegerField(validators=(MinValueValidator(1),))
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    tags = models.ManyToManyField(Tag, related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe', related_name='recipes'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipe'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredient_recipe'
    )
    amount = models.SmallIntegerField(validators=(MinValueValidator(1),))

    class Meta:
        verbose_name = 'Связь ингредиент-рецепт'
        verbose_name_plural = 'Связи ингредиент-рецепт'
        constraints = (
            UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique_ingredient_recipe'
            ),
        )

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name} ({self.amount})'


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
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shoping_cart'
            ),
        )

    def __str__(self):
        return f'{self.user.username} {self.recipe.name}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'{self.user.username} {self.recipe.name}'
