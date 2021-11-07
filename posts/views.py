from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

@cache_page(10, key_prefix="index_page")
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.

    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )

# view-функция для страницы сообщества
def group_posts(request, slug):
    # функция get_object_or_404 получает по заданным критериям объект из базы данных
    # или возвращает сообщение об ошибке, если объект не найден
    group = get_object_or_404(Group, slug=slug)

    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    post_list = group.posts.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "group.html", {"group": group,
                                          "page": page,
                                          "paginator": paginator})


@login_required()
def new_post(request):

    if request.method == 'POST':
        form = PostForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=author).order_by("-pub_date").all()
    post_count = user_posts.count()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {"author": author,
                                            "post_count": post_count,
                                            'following': following,
                                            "page": page,
                                            "paginator": paginator})

@cache_page(3)
def post_view(request, username, post_id):
    user_post = get_object_or_404(Post.objects.select_related('author'), author__username=username, id=post_id)
    author = user_post.author
    post_count = Post.objects.filter(author=user_post.author).all().count()
    form = CommentForm()
    comments = user_post.comments.all()
    return render(request, 'post.html', {"user_post": user_post,
                                         "author": author,
                                         "post_count": post_count,
                                         "form": form,
                                         "comments": comments})

@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post, author__username=username, id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST or None, request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
        return render(request, 'new_post.html', {'post': post, 'form': form})
    else:
        form = PostForm(instance=post)
    return render(request, 'new_post.html', {'post': post, 'form': form})

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post', username, post_id)
        return render(request, 'included/comments.html', {'form': form, "post": post})
    return redirect('post', username, post_id)

@login_required
def follow_index(request):
    following = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(following, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page,
                                           "paginator": paginator
                                           })

@login_required
def profile_follow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=follower, author=following)
    if follower != following and not follow.exists():
        Follow.objects.create(user=follower, author=following).save()
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=follower, author=following)
    if follower != following and follow.exists():
        follow.delete()
    return redirect('profile', username=username)

def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )

def server_error(request):
    return render(request, "misc/500.html", status=500)

