from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def make_pagination(request, object_list, per_page):
    paginator = Paginator(object_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    page = make_pagination(request, post_list, settings.PAGINATOR_PAGES)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page = make_pagination(request, post_list, settings.PAGINATOR_PAGES)
    return render(request, 'group.html', {'page': page, 'group': group})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    post_list = Post.objects.filter(author=author)
    page = make_pagination(request, post_list, settings.PAGINATOR_PAGES)
    following = user.is_authenticated and (
        Follow.objects.filter(user=user, author=author).exists())
    context = {
        'author': author,
        'page': page,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post.objects.select_related('author'),
                             id=post_id, author__username=username)
    form = CommentForm(instance=None)
    comments = post.comments.select_related('author').all()
    return render(request, 'post.html',
                  {'author': post.author,
                   'post': post,
                   'comments': comments,
                   'form': form})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new_post.html',
                      {'form': form, 'mode': 'create'})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username=username, post_id=post_id)
    post = get_object_or_404(Post.objects.select_related('author'),
                             id=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect(
            'post', username=username, post_id=post_id
        )
    return render(request, 'comments.html', {'author': post.author,
                                             'post': post,
                                             'comments': comments,
                                             'form': form})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page = make_pagination(request, post_list, settings.PAGINATOR_PAGES)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
        return redirect('index')
    return redirect('profile', username=author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        follow_list = Follow.objects.filter(author=author, user=request.user)
        follow_list.delete()
        return redirect('index')
    return redirect('profile', username=author.username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
