from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'published_at', 'created_at']
    list_filter = ['is_published', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'category']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['slug', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'category')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_alt_text')
        }),
        ('Publishing', {
            'fields': ('is_published', 'author', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
