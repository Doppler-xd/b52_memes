from django.db import models
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models.signals import post_save
from django.dispatch import receiver


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
    """Шаблоны мемов"""
    name = models.CharField(max_length=200, verbose_name="Название шаблона")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='samples', verbose_name="Категория")
    image = models.ImageField(upload_to='meme_templates/', verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Шаблон"
        verbose_name_plural = "Шаблоны"


class Mem(models.Model):
    """Мемы пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mems', verbose_name="Пользователь")
    sample = models.ForeignKey(Sample, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name="Шаблон", related_name='mems')
    custom_image = models.ImageField(upload_to='user_memes/', null=True, blank=True, verbose_name="Своё изображение")
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


def get_template_api(request, template_id):
    """API для получения информации о шаблоне"""
    try:
        template = Sample.objects.get(id=template_id)

        # Проверяем, существует ли изображение
        if not template.image:
            return JsonResponse({
                'error': 'Изображение шаблона не найдено'
            }, status=404)

        image_url = request.build_absolute_uri(template.image.url)

        return JsonResponse({
            'id': template.id,
            'name': template.name,
            'category': template.category.name,
            'image_url': image_url,
            'created_at': template.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Sample.DoesNotExist:
        return JsonResponse({
            'error': 'Шаблон не найден'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)