from django.contrib import admin
from .models import Category, Mem, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Mem)
class MemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'sample_id', 'created_at', 'is_public')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'user__username')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'bio')