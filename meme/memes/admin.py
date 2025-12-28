from django.contrib import admin
from .models import Category, Sample, Mem, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'image_name', 'created_at')  # ← добавлено image_name
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    # Если хочешь — можно добавить редактирование image_name в форме:
    # fields = ('name', 'category', 'image_name')


@admin.register(Mem)
class MemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'sample', 'created_at', 'is_public')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'user__username')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'bio')