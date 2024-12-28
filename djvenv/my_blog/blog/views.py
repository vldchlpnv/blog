from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from .forms import *
from .models import *
from django.views.decorators.http import require_POST  # декоратор @require_POST разрешит функии
# делать запросы только методом PОST
from taggit.models import Tag

def post_list(request, tag_slug=None):
    posts_list = Post.published.all()

    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_list = posts_list.filter(tags__in=[tag])


    paginator = Paginator(posts_list, 7)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(1)
    except PageNotAnInteger:
        posts = paginator.page(1)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag':tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts':similar_posts})

def post_share(request, post_id):

    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absilut_url)
            subject = f"{cd['name']} рекомендую прочитать {post.title}"
            message = f"Читай <{post.title}> по ссылке {post_url}" \
                      f" {cd['name']}, {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent':sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})




