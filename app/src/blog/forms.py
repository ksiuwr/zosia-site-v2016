from django import forms

from blog.models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        exclude = ['publication']
