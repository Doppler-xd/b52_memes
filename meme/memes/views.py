from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Mem, Profile
from django.db import OperationalError
import re
from django.utils.html import escape
from django.contrib import messages
import base64
import time
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


# === СТАТИЧНЫЕ ШАБЛОНЫ МЕМОВ ===
STATIC_TEMPLATES = [
    {"id": 1, "name": "Арнольд", "category": "Кино", "image_name": "arnold.jpg"},
    {"id": 2, "name": "Элайн", "category": "Сериалы", "image_name": "elaine.jpg"},
    {"id": 3, "name": "Дурачок", "category": "Мемы", "image_name": "dumbass.jpg"},
    # ДОБАВЬ СВОИ ФАЙЛЫ ЗДЕСЬ → точно как в static/meme_templates/
]


def home(request):
    """Главная страница"""
    popular_templates = STATIC_TEMPLATES[:8]
    return render(request, 'memes/home.html', {
        'popular_templates': popular_templates,
    })


@login_required
def user_memes(request):
    """Отображение мемов текущего пользователя"""
    mems = Mem.objects.filter(user=request.user)
    return render(request, 'memes/user_memes.html', {'mems': mems})


def template_gallery(request):
    """Страница галереи шаблонов мемов"""
    category_id = request.GET.get('category', 'all')
    query = request.GET.get('q', '')

    templates = STATIC_TEMPLATES
    if category_id != 'all':
        templates = [t for t in templates if t['category'] == category_id]
    if query:
        templates = [t for t in templates if query.lower() in t['name'].lower()]

    categories = sorted(set(t['category'] for t in STATIC_TEMPLATES))
    return render(request, 'memes/gallery.html', {
        'templates': templates,
        'categories': categories,
        'selected_category': category_id,
        'search_query': query,
    })


@method_decorator(login_required, name='dispatch')
class MemeEditorView(View):
    """Редактор мема: отображение и сохранение"""

    def get(self, request, template_id=None):
        template = None
        templates = STATIC_TEMPLATES[:8]
        if template_id:
            template = next((t for t in STATIC_TEMPLATES if t['id'] == template_id), None)

        return render(request, 'memes/editor.html', {
            'template': template,
            'templates': templates,
        })


@login_required
def save_meme_image(request):
    """Сохранение мема через AJAX (изображение)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image_data')

            if not image_data:
                return JsonResponse({
                    'success': False,
                    'error': 'Нет данных изображения'
                }, status=400)

            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file = ContentFile(
                base64.b64decode(imgstr),
                name=f'meme_{request.user.id}_{int(time.time())}.{ext}'
            )

            meme = Mem.objects.create(
                user=request.user,
                name=f"Мем #{Mem.objects.count() + 1}",
                custom_image=image_file,
                is_public=False
            )

            return JsonResponse({
                'success': True,
                'message': 'Мем сохранен',
                'meme_id': meme.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Метод не разрешен'}, status=405)


@login_required
def delete_meme(request, meme_id):
    """Удаление мема"""
    if request.method == 'POST':
        meme = get_object_or_404(Mem, id=meme_id, user=request.user)
        meme.delete()
        return redirect('memes:user_memes')
    return JsonResponse({'status': 'error', 'message': 'Неверный метод'}, status=400)


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        user = request.user
        raw_username = request.POST.get('username', user.username).strip()
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9_\.\-\s]{1,30}$', raw_username):
            messages.error(request,
                           'Имя пользователя может содержать только буквы, цифры, пробелы, точки, дефисы и подчёркивания.')
            return render(request, 'memes/edit_profile.html', {'user': request.user})

        user.username = escape(raw_username)[:30]
        user.email = request.POST.get('email', user.email)

        profile, created = Profile.objects.get_or_create(user=user)

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        if 'bio' in request.POST:
            profile.bio = request.POST['bio']

        user.save()
        profile.save()
        return redirect('memes:profile_page')

    return render(request, 'memes/edit_profile.html')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Почта')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('memes:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_page(request):
    """Страница профиля пользователя"""
    mems = Mem.objects.filter(user=request.user)
    return render(request, 'memes/profile.html', {
        'mems': mems,
        'user': request.user
    })


@csrf_exempt
def get_template_api(request):
    """API для получения списка шаблонов (из статики)"""
    category_id = request.GET.get('category', 'all')
    query = request.GET.get('q', '')

    templates = STATIC_TEMPLATES
    if category_id != 'all':
        templates = [t for t in templates if t['category'] == category_id]
    if query:
        templates = [t for t in templates if query.lower() in t['name'].lower()]

    templates_data = []
    for t in templates:
        templates_data.append({
            'id': t['id'],
            'name': t['name'],
            'category_name': t['category'],
            'image_url': f"/static/meme_templates/{t['image_name']}",
            'editor_url': f'/memes/editor/{t["id"]}/'
        })

    categories_data = [{"id": cat, "name": cat} for cat in sorted(set(t['category'] for t in STATIC_TEMPLATES))]

    return JsonResponse({
        'success': True,
        'templates': templates_data,
        'categories': categories_data,
        'selected_category': category_id,
        'search_query': query,
        'count': len(templates_data)
    })


@csrf_exempt
def get_template_detail_api(request, template_id):
    """API для получения информации о шаблоне по ID (из статики)"""
    template = next((t for t in STATIC_TEMPLATES if t['id'] == template_id), None)
    if not template:
        return JsonResponse({'error': 'Шаблон не найден'}, status=404)

    return JsonResponse({
        'id': template['id'],
        'name': escape(template['name']),
        'category': template['category'],
        'image_url': f"/static/meme_templates/{template['image_name']}",
        'created_at': '2025-01-01 00:00:00'
    })