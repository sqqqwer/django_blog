from datetime import datetime

from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.views.generic import (ListView, DetailView, UpdateView,
                                  DeleteView, CreateView)
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Category, Comment
from .forms import PostForm, UserProfileChangeForm, CommentForm

SHOW_POSTS_PAGINATION = 10
# User
User = get_user_model()


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
            pub_date__lte=datetime.now(),
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
                pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class CommentAuthorRequredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        comment_id = kwargs['pk']
        if request.user.is_authenticated:
            get_object_or_404(request.user.comments, pk=comment_id)
        return super().dispatch(request, *args, **kwargs)


class PostListMixin(ListView):
    model = Post
    paginate_by = SHOW_POSTS_PAGINATION


class PostListView(ValidPostQueryMixin, PostListMixin):
    template_name = 'blog/index.html'


class PostDetailView(PostQueryMixin, DetailView):
    template_name = 'blog/detail.html'
    model = Post

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        post = get_object_or_404(queryset, pk=self.kwargs.get('pk'))
        if post.author != self.request.user:
            queryset = ValidPostQueryMixin.valid_filters(queryset)
            post = get_object_or_404(queryset, pk=self.kwargs.get('pk'))
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

    def form_valid(self, form):
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs.get('post_pk')
        )
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentEditView(CommentAuthorRequredMixin, UpdateView):
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm


class CommentDeleteView(CommentAuthorRequredMixin, DeleteView):
    template_name = 'blog/comment.html'
    model = Comment

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_pk')}
        )


class PostCreateView(
    SuccessRedirectProfileMixin,
    LoginRequiredMixin,
    CreateView
):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(PostAuthorRequredMixin, UpdateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm


class PostDeleteView(
    SuccessRedirectProfileMixin,
    PostAuthorRequredMixin,
    DeleteView
):
    template_name = 'blog/create.html'
    model = Post


class CategoryPostListView(ValidPostQueryMixin, PostListMixin):
    template_name = 'blog/category.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            category__slug=self.kwargs.get('slug')
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs.get('slug')
        )
        context['category'] = category
        return context


class UserProfilePostListView(PostQueryMixin, PostListMixin):
    template_name = 'blog/profile.html'

    def get_queryset(self):
        user_profile_username = self.kwargs.get('username')

        queryset = super().get_queryset().filter(
            author__username=user_profile_username
        )
        if self.request.user.username != user_profile_username:
            queryset = ValidPostQueryMixin.valid_filters(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(User, username=self.kwargs.get('username'))
        context['profile'] = profile
        return context


class UserProfileEditView(
    SuccessRedirectProfileMixin,
    LoginRequiredMixin,
    UpdateView
):
    def get_object(self):
        return self.request.user
    template_name = 'blog/user.html'
    model = User
    form_class = UserProfileChangeForm
