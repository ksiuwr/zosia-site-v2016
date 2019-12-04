from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie

from questions.forms import QAForm
from questions.models import QA
from utils.forms import errors_format


@cache_page(60 * 60 * 24)
@vary_on_cookie
@require_http_methods(['GET'])
def index(request):
    qas = QA.objects.all()
    ctx = {'questions': qas}
    return render(request, 'questions/index.html', ctx)


@require_http_methods(['GET'])
@staff_member_required()
def index_for_staff(request):
    qas = QA.objects.all()
    ctx = {'questions': qas}
    return render(request, 'questions/index_staff.html', ctx)


@require_http_methods(['GET', 'POST'])
@staff_member_required()
def update(request, question_id=None):
    kwargs = {}
    if question_id is not None:
        question = get_object_or_404(QA, pk=question_id)
        kwargs['instance'] = question
    else:
        question = None

    form = QAForm(request.POST or None, **kwargs)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('questions_index_staff')
        else:
            messages.error(request, errors_format(form))

    ctx = {'form': form, 'question': question}
    return render(request, 'questions/update.html', ctx)


@require_http_methods(['GET'])
@staff_member_required()
def delete(request, question_id):
    question = get_object_or_404(QA, pk=question_id)
    question.delete()
    return redirect('questions_index_staff')
