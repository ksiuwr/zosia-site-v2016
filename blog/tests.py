from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import BlogPost

User = get_user_model()


class ModelTestCase(TestCase):
    def setUp(self):
        self.normal = User.objects.create_user('john', 'lennon@thebeatles.com',
                                               'johnpassword')
        self.normal.save()

        self.staff = User.objects.create_user('paul', 'paul@thebeatles.com',
                                              'paulpassword')
        self.staff.is_staff = True
        self.staff.save()

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
