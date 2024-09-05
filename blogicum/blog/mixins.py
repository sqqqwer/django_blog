from django.utils import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.urls import reverse

from .models import Post


SHOW_POSTS_PAGINATION = 10


class PostQueryMixin:
    queryset = Post.objects.select_related(
        'author', 'category', 'location'
    )

    def get_queryset(self):
        return self.queryset


class SuccessRedirectProfileMixin:
    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class ValidPostQueryMixin(PostQueryMixin):
    @classmethod
    def valid_filters(cls, queryset):
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.valid_filters(queryset)
        return queryset


class PostAuthorRequredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect(
                'blog:post_detail',
                post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentAuthorRequredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        comment_id = kwargs[self.pk_url_kwarg]
        if request.user.is_authenticated:
            get_object_or_404(request.user.comments, pk=comment_id)
        return super().dispatch(request, *args, **kwargs)


class PostListMixin(ListView):
    model = Post
    paginate_by = SHOW_POSTS_PAGINATION
