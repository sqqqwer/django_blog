from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (
    DetailView,
    UpdateView,
    DeleteView,
    CreateView
)
from django.urls import reverse

from .forms import PostForm, UserProfileChangeForm, CommentForm
from . import mixins
from .models import Post, Category, Comment


User = get_user_model()


class PostListView(mixins.ValidPostQueryMixin, mixins.PostListMixin):
    template_name = 'blog/index.html'


class PostDetailView(mixins.ValidPostQueryMixin, DetailView):
    template_name = 'blog/detail.html'
    model = Post
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        queryset = self.queryset

        post = get_object_or_404(queryset,
                                 pk=self.kwargs.get(self.pk_url_kwarg))
        if post.author != self.request.user:
            queryset = self.get_queryset()
            post = get_object_or_404(queryset,
                                     pk=self.kwargs.get(self.pk_url_kwarg))
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related(
            'author'
        ).all()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs.get(self.pk_url_kwarg)
        )
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentEditView(mixins.CommentAuthorRequredMixin, UpdateView):
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'


class CommentDeleteView(mixins.CommentAuthorRequredMixin, DeleteView):
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class PostCreateView(
    mixins.SuccessRedirectProfileMixin,
    LoginRequiredMixin,
    CreateView
):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(mixins.PostAuthorRequredMixin, UpdateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'


class PostDeleteView(
    mixins.SuccessRedirectProfileMixin,
    mixins.PostAuthorRequredMixin,
    DeleteView
):
    template_name = 'blog/create.html'
    model = Post
    pk_url_kwarg = 'post_id'


class CategoryPostListView(mixins.ValidPostQueryMixin, mixins.PostListMixin):
    template_name = 'blog/category.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            category__slug=self.kwargs.get('category_slug')
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs.get('category_slug')
        )
        context['category'] = category
        return context


class UserProfilePostListView(mixins.PostQueryMixin, mixins.PostListMixin):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        user_profile_username = self.kwargs.get('username')

        queryset = super().get_queryset().filter(
            author__username=user_profile_username
        )
        if self.request.user.username != user_profile_username:
            queryset = mixins.ValidPostQueryMixin.valid_filters(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(User, username=self.kwargs.get('username'))
        context['profile'] = profile
        return context


class UserProfileEditView(
    mixins.SuccessRedirectProfileMixin,
    LoginRequiredMixin,
    UpdateView
):
    template_name = 'blog/user.html'
    model = User
    form_class = UserProfileChangeForm

    def get_object(self):
        return self.request.user
