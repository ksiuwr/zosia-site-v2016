from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from questions.forms import QAForm
from questions.models import QA
from utils.test_helpers import create_user, login_as_user

User = get_user_model()


class FormTestCase(TestCase):
    def test_no_data(self):
        form = QAForm()
        self.assertFalse(form.is_valid())

    def test_create_object(self):
        count = QA.objects.count()
        form = QAForm({'question': 'foo', 'answer': 'bar', 'priority': 0})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(count + 1, QA.objects.count())


class ViewsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.staff = create_user(0, is_staff=True)
        self.normal = create_user(1)

    def test_index_get_no_user(self):
        response = self.client.get(reverse('questions_index_staff'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/questions/all/')

    def test_index_get_normal_user(self):
        login_as_user(self.normal, self.client)
        response = self.client.get(reverse('questions_index_staff'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/questions/all/')

    def test_index_get_staff_user(self):
        login_as_user(self.staff, self.client)
        response = self.client.get(reverse('questions_index_staff'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['questions']), list(QA.objects.all().order_by('-priority')))

    def test_add_get_staff_user(self):
        login_as_user(self.staff, self.client)
        response = self.client.get(reverse('questions_add'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, QAForm)

    def test_add_post(self):
        questions = QA.objects.count()
        login_as_user(self.staff, self.client)
        response = self.client.post(reverse('questions_add'),
                                    {'question': 'foo', 'answer': 'bar', 'priority': 0},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(questions + 1, QA.objects.count())

    def test_edit_get_staff_user(self):
        login_as_user(self.staff, self.client)
        qa = QA.objects.create(question='foo', answer='http://google.com')
        response = self.client.get(reverse('questions_edit',
                                           kwargs={'question_id': qa.id}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, QAForm)
        self.assertEqual(context['question'], qa)
