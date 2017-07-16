from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from .models import BlogPost
from .forms import BlogPostForm


@require_http_methods(['GET'])
def index(request):
    ctx = {'posts': BlogPost.objects.select_related('author').all()}
    return render(request, 'blog/index.html', ctx)


@staff_member_required
@require_http_methods(['GET', 'POST'])
def create(request):
    ctx = {'form': BlogPostForm(request.POST or None)}

    if request.method == 'POST':
        if ctx['form'].is_valid():
            ctx['form'].save()
            return redirect('blog_index')
    return render(request, 'blog/create.html', ctx)
