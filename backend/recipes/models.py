from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField
from pytils.translit import slugify

from recipes.constants import MAX_LENGTH
from recipes.strings import MSG_LETTERS_RU, MSG_LETTERS_US, MSG_NUM
from users.models import User


class Tag(models.Model):
    """
    Модель таблицы тэга.
    Attributes:
        name: CharField - название тэга
        color: ColorField - цвет тега, в формате HEX
        slug: SlugField - кратное название латиницей
    """

    name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH,
        unique=True,
        help_text=(
            'Введите название тэга.'
            f'{MSG_LETTERS_RU}'
        ),
    )
    color = ColorField(
        verbose_name='HEX-код',
        format='hex',
        default='#FF0000',
        help_text='Введите цвет в HEX-формате.',
    )
    slug = models.SlugField(
        verbose_name='Короткое название',
        max_length=MAX_LENGTH,
        unique=True,
        help_text=(
            'Укажите уникальный адрес тэга.'
            f'{MSG_LETTERS_US}'
        ),
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['-id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:MAX_LENGTH]
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    """
    Модель таблицы ингредиента.
    Attributes:
        name: CharField - название ингредиента
        measurement_unit: CharField - единица измерения ингредиента
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH,
        db_index=True,
        help_text=(
            'Введите название ингредиента.'
            f'{MSG_LETTERS_RU}'
        ),
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=MAX_LENGTH,
        default='г',
        help_text=(
            'Введите единицу измерения для данного ингредиента.'
            f'{MSG_NUM}'
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель таблицы рецепта.
    Attributes:
        author : ForeignKey - ссылка (ID) на объект класса User
        name: CharField - название рецепта
        image: ImageField - изображение рецепта
        text: CharField - описание рецепта
        ingredients: ManyToManyField - ссылка на промежуточную модель 
            ингредиентов
        tags: ForeignKey - ссылка (ID) на объект класса Tag
        cooking_time: PositiveSmallIntegerField - время приготовления 
            (положительное число)
        pub_date: DateTimeField - дата создания
    """

    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Введите id автора рецепта.',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH,
        help_text=(
            'Введите название рецепта.'
            f'{MSG_LETTERS_RU}'
        ),
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="static/recipe/",
        blank=True,
        null=True,
        help_text="Здесь можно загрузить картинку, объёмом не более 5Мб",
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text=(
            'Опишите ваш творение.'
            f'{MSG_LETTERS_RU}'
        ),
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientAmount',
        related_name='ingredients',
        help_text='Введите id ингредиентов, для приготовления блюда',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
        help_text='Введите id ассоциирующегося тега.',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1, 'Время приготовления не может быть меньше 1 минуты!'
            ),
        ],
        default=1,
        help_text='Введите время необходимое для приготовления в минутах.',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания рецепта',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    """
    Модель таблицы количества ингредиента.
    Attributes:
        ingredient: ForeignKey - ссылка (ID) на объект класса Ingredient
        recipe: ForeignKey - ссылка (ID) на объект класса Recipe
        amount: DecimalField - количество иингредиента положительное
            целое/десятичное число
    """

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='amount_ingredient',
        help_text=(
            'Введите название ингредиента.'
            f'{MSG_LETTERS_RU}'
        ),
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='amount_ingredient',
        help_text='Введите Id рецепта.',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=(
            MinValueValidator(
                1, message='Мин. количество ингридиентов 1'),),
        help_text='Введите необходимое количество ингредиента.',
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return f'{self.amount} of {self.ingredient}'


class FavoriteRecipe(models.Model):
    """
    Модель таблицы избранных рецептов.
    Attributes:
        user: ForeignKey - ссылка (ID) на объект класса User
        recipe: ForeignKey - ссылка (ID) на объект класса Recipe
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
        help_text='Введите Id любимого рецепта.',
    )

    class Meta:
        verbose_name = 'Список избранного'
        verbose_name_plural = 'Списки избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorites'
            )
        ]

    def __str__(self):
        return f'Favorite recipe {self.recipe} {self.user}'


class ShoppingCart(models.Model):
    """
    Модель таблицы корзины покупок.
    Attributes:
        user: ForeignKey - ссылка (ID) на объект класса User
        recipe: ForeignKey - ссылка (ID) на объект класса Recipe
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        help_text='Введите Id рецепта который хотите добавить в корзину.',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
