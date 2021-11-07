from django.contrib import admin

from .models import Post, Group, Comment


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    empty_value_display = "-пусто-"

class PostAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("pk", "text", "pub_date", "author")
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",)
    # добавляем возможность фильтрации по дате
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"  # это свойство сработает для всех колонок: где пусто - там будет эта строка

class CommentForm(admin.ModelAdmin):
    list_display = ("pk", "post", "author", "text", "created")
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"

# при регистрации модели Post источником конфигурации для неё назначаем класс PostAdmin
admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentForm)
