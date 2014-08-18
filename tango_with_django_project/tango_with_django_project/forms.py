from django import forms
from rango.models import Category, Page

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Category

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter page title.")
    url = forms.URLField(max_length=200, help_text="Please enter URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput, initial=0)

    class Meta:
        model = Page
        # fields = ('title', 'url', 'views')