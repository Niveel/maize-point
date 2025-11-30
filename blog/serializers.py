from rest_framework import serializers
from .models import BlogPost


class BlogPostSerializer(serializers.ModelSerializer):
    """Serializer for BlogPost model"""
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'featured_image', 'image_alt_text',
                  'category', 'is_published', 'author', 'author_name', 'published_at',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'author', 'published_at', 'created_at', 'updated_at']
