from django.urls import path
from . import views

app_name = 'memes'

urlpatterns = [
    path('', views.home, name='home'),
    path('memes/', views.user_memes, name='user_memes'),
    path('memes/gallery/', views.template_gallery, name='gallery'),
    path('memes/editor/', views.MemeEditorView.as_view(), name='editor_new'),
    path('memes/editor/<int:template_id>/', views.MemeEditorView.as_view(), name='editor_with_template'),
    path('memes/save/', views.save_meme_image, name='save_meme_image'),
    path('memes/delete/<int:meme_id>/', views.delete_meme, name='delete_meme'),
    path('memes/profile/edit/', views.edit_profile, name='edit_profile'),
    path('memes/profile/', views.profile_page, name='profile_page'),
    path('memes/register/', views.register, name='register'),
    
    # API endpoints
    path('memes/api/templates/', views.get_template_api, name='api_templates'),
    path('memes/api/template/<int:template_id>/', views.get_template_detail_api, name='api_template_detail'),
]