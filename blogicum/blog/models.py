from django.contrib.auth import get_user_model
from django.db import models
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
        return self.title[:10]


class Location(IspublishedInfoModel, PubDateInfoModel):
    name = models.CharField('Название места',
                            max_length=LOCATION_NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:10]


class Post(IspublishedInfoModel, PubDateInfoModel):
    pub_date_help_text = ('Если установить дату и время в будущем '
                          '— можно делать отложенные публикации.')

    title = models.CharField('Заголовок', max_length=POST_TITLE_MAX_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата и время публикации',
                                    help_text=pub_date_help_text)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    category = models.ForeignKey('Category',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория')
    location = models.ForeignKey('Location',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=False,
                                 verbose_name='Местоположение')
    image = models.ImageField('Изображение',
                              upload_to='post_image',
                              blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'

        ordering = ('-pub_date',)

    @property
    def comment_count(self):
        return self.comments.count()

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.id})

    def __str__(self):
        return self.title[:12]


class Comment(PubDateInfoModel):
    text = models.TextField('Текст')

    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             verbose_name='Комментарий Публикации')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор Комментария')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

        default_related_name = 'comments'

        ordering = ('created_at',)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.post.id})

    def __str__(self):
        return f'{self.post.id} - {self.text}'[:15]
