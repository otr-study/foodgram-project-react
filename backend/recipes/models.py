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
        constraints = (
            UniqueConstraint(
                fields=('tag', 'recipe',),
                name='unique_tag_recipe'
            ),
        )

    def __str__(self):
        return f'{self.tag} - {self.recipe}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()

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
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shoping_cart'
            ),
        )

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
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'{self.user} {self.recipe}'
