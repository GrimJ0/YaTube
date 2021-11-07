from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):

    title = models.CharField(verbose_name='Название сообщества', max_length=100)
    slug = models.SlugField(verbose_name='Адрес',
                            help_text='Задайте уникальный адрес сообщества',
                            unique=True)
    description = models.TextField(verbose_name='Описание', help_text='Опишите группу')

    def __str__(self):
        return self.title


class Post(models.Model):

    group = models.ForeignKey(
                            Group, blank=True, null=True,
                            related_name="posts",
                            on_delete=models.SET_NULL,
                            verbose_name='Сообщество',
                            help_text='Выберите группу'
                            )
    title = models.CharField(verbose_name='Заголовок', max_length=100, unique=True)
    text = models.TextField(verbose_name='Текст поста', help_text='Введите текст вашего поста')
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", verbose_name='Автор')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Изображение',
                              help_text='Добавьте изображение к посту'
                              )

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name='Пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", verbose_name='Автор')
    text = models.TextField(verbose_name='Комментария', help_text='Введите ваш комментарий')
    created = models.DateTimeField("Дата публикации", auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower", verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'