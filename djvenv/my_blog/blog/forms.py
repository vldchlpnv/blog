from django import forms
from django.forms import ModelForm
from .models import Comment



class EmailPostForm(forms.Form):

    name = forms.CharField(max_length=25, label='', help_text='Имя')
    email = forms.EmailField(label='', help_text='Электронная почта отправителя') # от кого
    to = forms.EmailField(label='', help_text='Электронная почта получателя') # кому
    comments = forms.CharField(required=False,
                               widget=forms.Textarea, label='', help_text='Комментарий')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']