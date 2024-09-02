from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import IspublishedInfoModel, PubDateInfoModel

CATEGORY_TITLE_MAX_LENGTH = 256
LOCATION_NAME_MAX_LENGTH = 256
POST_TITLE_MAX_LENGTH = 256

User = get_user_model()


class Category(IspublishedInfoModel, PubDateInfoModel):
    slug_help_text = ('Идентификатор страницы для URL; разрешены '
                      'символы латиницы, цифры, дефис и подчёркивание.')

    title = models.CharField('Заголовок',
                             max_length=CATEGORY_TITLE_MAX_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField('Идентификатор',
                            unique=True,
                            help_text=slug_help_text)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(IspublishedInfoModel, PubDateInfoModel):
    name = models.CharField('Название места',
                            max_length=LOCATION_NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(IspublishedInfoModel, PubDateInfoModel):
    POST_RELATED_NAME = 'posts'

    pub_date_help_text = ('Если установить дату и время в будущем '
                          '— можно делать отложенные публикации.')

    title = models.CharField('Заголовок', max_length=POST_TITLE_MAX_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата и время публикации',
                                    help_text=pub_date_help_text)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name=POST_RELATED_NAME,
                               verbose_name='Автор публикации')
    category = models.ForeignKey('Category',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name=POST_RELATED_NAME,
                                 verbose_name='Категория')
    location = models.ForeignKey('Location',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=False,
                                 related_name=POST_RELATED_NAME,
                                 verbose_name='Местоположение')
    image = models.ImageField('Изображение',
                              upload_to='post_image',
                              blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.id})

    @property
    def comment_count(self):
        return self.comments.count()


class Comment(PubDateInfoModel):
    COMMENT_RELATED_NAME = 'comments'
    text = models.TextField('Текст')

    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name=COMMENT_RELATED_NAME,
                             verbose_name='Комментарий Публикации')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name=COMMENT_RELATED_NAME,
                               verbose_name='Автор Комментария')

    class Meta:
        ordering = ('created_at',)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post.id})
