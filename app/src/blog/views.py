from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext_lazy as _

from blog.forms import BlogPostForm
from blog.models import BlogPost


@require_http_methods(['GET'])
def index(request):
    ctx = {'posts': BlogPost.objects.select_related('author').all()}
    return render(request, 'blog/index.html', ctx)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def create(request):
    form = BlogPostForm(request.POST or None)
    ctx = {'form': form}

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('blog_index')
    return render(request, 'blog/create.html', ctx)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def list(request):
    ctx = {'posts': BlogPost.objects.select_related('author').all()}
    return render(request, 'blog/list.html', ctx)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def edit(request, pk=None):
    if pk is not None:
        post = get_object_or_404(BlogPost, pk=pk)
        form = BlogPostForm(request.POST or None, instance=post)
    else:
        post = None
        form = BlogPostForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, _('Post updated'))
        return redirect('blog_list')

    ctx = {'form': form, 'post': post}
    return render(request, 'blog/create.html', ctx)
