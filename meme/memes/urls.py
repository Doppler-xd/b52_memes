from django.urls import path
from . import views

app_name = 'memes'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # Галерея шаблонов
    path('gallery/', views.template_gallery, name='gallery'),

    # Редактор мемов
    path('editor/', views.MemeEditorView.as_view(), name='editor_new'),
    path('editor/<int:template_id>/', views.MemeEditorView.as_view(), name='editor_with_template'),

    # API для сохранения изображений
    path('api/save-meme-image/', views.save_meme_image, name='save_meme_image'),

    # Мемы пользователя
    path('my-memes/', views.user_memes, name='user_memes'),
    path('delete/<int:meme_id>/', views.delete_meme, name='delete_meme'),

    # Профиль
    path('profile/', views.profile_page, name='profile_page'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    # Регистрация
    path('register/', views.register, name='register'),
    path('api/template/<int:template_id>/', views.get_template_detail_api, name='get_template_detail_api'),
    path('api/templates/', views.get_template_api, name='get_templates_api')
]