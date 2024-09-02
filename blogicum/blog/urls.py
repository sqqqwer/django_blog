from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:pk>/edit/',
        views.PostEditView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_pk>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_pk>/edit_comment/<int:pk>/',
        views.CommentEditView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_pk>/delete_comment/<int:pk>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'profile/edit/',
        views.UserProfileEditView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<str:username>/',
        views.UserProfilePostListView.as_view(),
        name='profile'
    ),
    path(
        'category/<slug:slug>/',
        views.CategoryPostListView.as_view(),
        name='category_posts'
    ),
]
