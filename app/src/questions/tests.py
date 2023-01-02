from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from questions.models import QA
from questions.forms import QAForm


User = get_user_model()


class FormTestCase(TestCase):
    def test_no_data(self):
        form = QAForm()
        self.assertFalse(form.is_valid())

    def test_create_object(self):
        count = QA.objects.count()
        form = QAForm({'question': 'foo', 'answer': 'bar', 'priority': '0'})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(count + 1, QA.objects.count())


class ViewsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user('paul@thebeatles.com',
                                              'paulpassword')
        self.staff.is_staff = True
        self.staff.save()

        self.normal = User.objects.create_user('lennon@thebeatles.com',
                                               'johnpassword')
        self.normal.save()

    def test_index_get_no_user(self):
        response = self.client.get(reverse('questions_index_staff'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/questions/all/')

    def test_index_get_normal_user(self):
        self.client.login(email="lennon@thebeatles.com", password="johnpassword")
        response = self.client.get(reverse('questions_index_staff'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/questions/all/')

    def test_index_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        response = self.client.get(reverse('questions_index_staff'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(list(context['questions']), list(QA.objects.all().order_by('-priority')))

    def test_add_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        response = self.client.get(reverse('questions_add'), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, QAForm)

    def test_add_post(self):
        questions = QA.objects.count()
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        response = self.client.post(reverse('questions_add'),
                                    {'question': 'foo', 'answer': 'bar', 'priority': '0'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(questions + 1, QA.objects.count())

    def test_edit_get_staff_user(self):
        self.client.login(email='paul@thebeatles.com', password='paulpassword')
        qa = QA.objects.create(question='foo', answer='http://google.com')
        response = self.client.get(reverse('questions_edit',
                                           kwargs={'question_id': qa.id}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['form'].__class__, QAForm)
        self.assertEqual(context['question'], qa)
