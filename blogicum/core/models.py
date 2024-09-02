from django.db import models


class PubDateInfoModel(models.Model):
    created_at = models.DateTimeField('Добавлено',
                                      auto_now_add=True)

    class Meta:
        abstract = True


class IspublishedInfoModel(models.Model):
    is_published_help_text = 'Снимите галочку, чтобы скрыть публикацию.'

    is_published = models.BooleanField('Опубликовано',
                                       default=True,
                                       help_text=is_published_help_text)

    class Meta:
        abstract = True
