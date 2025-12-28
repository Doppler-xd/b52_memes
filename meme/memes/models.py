from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Категории шаблонов"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Sample(models.Model):
    """Шаблоны мемов — теперь статичные изображения из static/meme_templates/"""
    name = models.CharField(max_length=200, verbose_name="Название шаблона")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='samples',
        verbose_name="Категория"
    )
    image_name = models.CharField(
        max_length=255,
        verbose_name="Имя файла изображения",
        help_text="Например: arnold.jpg"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Шаблон"
        verbose_name_plural = "Шаблоны"


class Mem(models.Model):
    """Мемы пользователей (сохраняются в media)"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mems',
        verbose_name="Пользователь"
    )
    sample = models.ForeignKey(
        Sample,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Шаблон",
        related_name='mems'
    )
    custom_image = models.ImageField(
        upload_to='user_memes/',
        null=True,
        blank=True,
        verbose_name="Своё изображение"
    )
    name = models.CharField(max_length=200, verbose_name="Название", default='Мой мем')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_public = models.BooleanField(default=False, verbose_name="Публичный")

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    class Meta:
        verbose_name = "Мем"
        verbose_name_plural = "Мемы"


class Profile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name="Аватар"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"