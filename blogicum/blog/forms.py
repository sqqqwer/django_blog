from django.contrib.auth import get_user_model
from django.forms import ModelForm, DateTimeInput

from .models import Post, Comment


User = get_user_model()


class PostForm(ModelForm):
    class Meta:
        model = Post
        exclude = ['created_at', 'is_published', 'author']
        widgets = {
            'pub_date': DateTimeInput(
                format='%Y-%m-%dT%H:%M:%S',
                attrs={'type': 'datetime-local'}
            )
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserProfileChangeForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
