from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from questions.models import QA


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

