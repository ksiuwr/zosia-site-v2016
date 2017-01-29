from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from questions.models import QA
from questions.forms import QAForm


@require_http_methods(['GET'])
def index(request):
    qas = QA.objects.all()
    ctx = {'objects': qas}
    return render(request, 'questions/index.html', ctx)


@require_http_methods(['GET'])
@staff_member_required()
def index_for_staff(request):
    qas = QA.objects.all()
    ctx = {'questions': qas}
    return render(request, 'questions/index_staff.html', ctx)


@require_http_methods(['GET', 'POST'])
@staff_member_required()
def update(request, question_id):
    kwargs = {}
    if question_id:
        question = get_object_or_404(QA, pk=question_id)
        kwargs['question'] = question
    else:
        question = None

    form = QAForm(request.POST or None, **kwargs)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('questions_index')
        else:
            messages.error(request, _('There has been error'))
    ctx = {'form': form, 'question': question}
    return render(request, 'questions/update.html', ctx)
