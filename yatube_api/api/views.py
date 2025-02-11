from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets
from posts.models import Post, Group, Comment
from .serializers import PostSerializer, GroupSerializer, CommentSerializer


class BaseAuthority(viewsets.ModelViewSet):

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')

        return super().perform_destroy(instance)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')

        return super().perform_update(serializer)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(BaseAuthority):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        return serializer.save(
            author=self.request.user
        )


class CommentViewSet(BaseAuthority):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        return self.get_post_obj().comments.all()

    def get_post_obj(self):
        return get_object_or_404(
            Post,
            pk=self.kwargs.get('post_pk')
        )

    def perform_create(self, serializer):
        return serializer.save(
            author=self.request.user,
            post=self.get_post_obj()
        )
