from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields.related import ForeignKey

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255,
                            db_index=True, unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Текст страницы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE, related_name='posts')
    group = models.ForeignKey('Group',
                              on_delete=models.SET_NULL, blank=True,
                              null=True,
                              related_name='posts', verbose_name='Группа',
                              help_text='Выберите группу')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Изображение',
                              help_text='Добавьте картинку')

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(
        'Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Введите текст комментария')
    created = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pk',)


class Follow(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = ForeignKey(User, on_delete=models.CASCADE,
                        related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_list')
        ]
