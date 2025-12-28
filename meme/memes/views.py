from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Sample, Mem, Category, Profile
from django.db import OperationalError
import re
from django.utils.html import escape
from django.contrib import messages
import base64
import time
from django.core.files.base import ContentFile

def home(request):
    """Главная страница"""
    popular_templates = Sample.objects.all()[:8]
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

    templates = Sample.objects.all()
    if category_id != 'all':
        templates = templates.filter(category_id=category_id)
    if query:
        templates = templates.filter(name__icontains=query)

    categories = Category.objects.all()
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
        templates = []

        try:
            templates = Sample.objects.all()[:8]
            if template_id:
                template = get_object_or_404(Sample, id=template_id)
        except OperationalError as e:
            print(f"Database error: {e}")

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

            # Декодирование base64 изображения
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file = ContentFile(
                base64.b64decode(imgstr),
                name=f'meme_{request.user.id}_{int(time.time())}.{ext}'
            )

            # Сохранение мема в базу
            meme = Mem.objects.create(
                user=request.user,
                name=f"Мем #{meme.id}",
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

        # Защита от XSS при отображении (defence-in-depth)
        user.username = escape(raw_username)[:30]
        user.email = request.POST.get('email', user.email)

        # Получаем или создаем профиль
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
        'user': request.user  # передаем user в контекст
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def get_template_api(request):
    """API для получения списка шаблонов"""
    try:
        # Получаем параметры из запроса
        category_id = request.GET.get('category', 'all')
        query = request.GET.get('q', '')

        print(f"API called with category: {category_id}, query: {query}")  # Для отладки

        templates = Sample.objects.select_related('category').all()

        if category_id != 'all':
            try:
                category_id_int = int(category_id)
                templates = templates.filter(category_id=category_id_int)
                print(f"Filtering by category: {category_id_int}")  # Для отладки
            except (ValueError, TypeError) as e:
                print(f"Error parsing category_id: {e}")  # Для отладки
                pass

        if query:
            templates = templates.filter(name__icontains=query)
            print(f"Filtering by query: {query}")  # Для отладки

        # Преобразуем в JSON-совместимый формат
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'category_name': template.category.name if template.category else 'Без категории',
                'image_url': request.build_absolute_uri(template.image.url) if template.image else '',
                'editor_url': f'/memes/editor/{template.id}/'
            })

        categories_data = []
        for category in Category.objects.all():
            categories_data.append({
                'id': category.id,
                'name': category.name
            })

        response_data = {
            'success': True,
            'templates': templates_data,
            'categories': categories_data,
            'selected_category': category_id,
            'search_query': query,
            'count': len(templates_data)
        }

        print(f"API response: {response_data['count']} templates found")  # Для отладки

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        print(f"API error: {e}")  # Для отладки
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
def get_template_detail_api(request, template_id):
    """API для получения информации о шаблоне по ID"""
    try:
        template = get_object_or_404(Sample, id=template_id)

        if not template.image:
            return JsonResponse({
                'error': 'Изображение шаблона не найдено'
            }, status=404)

        return JsonResponse({
            'id': template.id,
            'name': escape(template.name),  # 🔒 экранируем!
            'category': escape(template.category.name) if template.category else None,
            'image_url': request.build_absolute_uri(template.image.url),
            'created_at': template.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)