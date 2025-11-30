from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import BlogPost
from .serializers import BlogPostSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for anyone, write for admins only"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.user_type == 'ADMIN'


class BlogPostViewSet(viewsets.ModelViewSet):
    """ViewSet for BlogPost model"""
    queryset = BlogPost.objects.select_related('author').all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_published']
    search_fields = ['title', 'content', 'category']
    ordering_fields = ['published_at', 'created_at']
    ordering = ['-published_at']
    lookup_field = 'slug'
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.user_type == 'ADMIN':
            return self.queryset
        # Public users see only published posts
        return self.queryset.filter(is_published=True)
    
    def perform_create(self, serializer):
        blog_post = serializer.save(author=self.request.user)
        if blog_post.is_published and not blog_post.published_at:
            blog_post.published_at = timezone.now()
            blog_post.save()
    
    def perform_update(self, serializer):
        blog_post = serializer.save()
        if blog_post.is_published and not blog_post.published_at:
            blog_post.published_at = timezone.now()
            blog_post.save()
