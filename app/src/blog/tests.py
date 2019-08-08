from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse

from blog.models import BlogPost
from blog.forms import BlogPostForm

User = get_user_model()


class BlogTests(TestCase):
    def setUp(self):
        self.normal = User.objects.create_user('lennon@thebeatles.com',
                                               'johnpassword')
        self.normal.save()

        self.staff = User.objects.create_user('paul@thebeatles.com',
                                              'paulpassword')
        self.staff.is_staff = True
        self.staff.save()


class ModelTestCase(BlogTests):

    def test_user_cannot_be_normal(self):
        count = BlogPost.objects.count()
        with self.assertRaises(ValidationError):
            post = BlogPost(author=self.normal, title="foo", content="bar")
            post.full_clean()
        self.assertEqual(count, BlogPost.objects.count())

    def test_user_must_be_staff(self):
        count = BlogPost.objects.count()
        BlogPost(author=self.staff, title='foo', content='bar').save()
        self.assertEqual(count + 1, BlogPost.objects.count())

    def test_model_str(self):
        foo = BlogPost(author=self.staff, title="foo", content="bar")
        foo.save()
        self.assertEqual("foo", str(foo))


class FormTestCase(BlogTests):
    def test_no_data(self):
        form = BlogPostForm()
        self.assertFalse(form.is_valid())

    def test_create_object(self):
        count = BlogPost.objects.count()
        form = BlogPostForm({'title': 'foo', 'content': 'bar', 'author': self.staff.id})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(count + 1, BlogPost.objects.count())

    def test_fail_normal_user(self):
        form = BlogPostForm({'title': 'foo', 'content': 'bar', 'author': self.normal.id})
        self.assertFalse(form.is_valid())


class ViewTestCase(BlogTests):
    def setUp(self):
        super().setUp()
        self.foo = BlogPost(author=self.staff, title='foo', content='bar')
        self.foo.save()

    def test_index(self):
        response = self.client.get(reverse('blog_index'), follow=True)
        context = response.context[-1]
        self.assertEqual(set(context['posts']), set(BlogPost.objects.all()))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/index.html')

    def test_create_get_no_user(self):
        response = self.client.get(reverse('blog_create'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/admin/login/?next=/blog/create')

    def test_create_get_staff_user(self):
        self.client.login(email="paul@thebeatles.com", password="paulpassword")
        response = self.client.get(reverse('blog_create'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/create.html')
        context = response.context[-1]
        self.assertTrue(isinstance(context['form'], BlogPostForm))

    def test_create_post(self):
        count = BlogPost.objects.count()
        response = self.client.post(reverse('blog_create'), {'author': self.normal.id, 'title': 'foo',
                                    'content': 'bar'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, BlogPost.objects.count())
