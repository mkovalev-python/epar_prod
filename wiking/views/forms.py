# -*- coding:utf-8 -*-
from django.core.validators import RegexValidator

__author__ = 'rayleigh'

from django import forms


class ArticleForm(forms.Form):
    title = forms.CharField(max_length=255, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control'}), label='Заголовок')
    slug = forms.CharField(max_length=255, required=True,
                           validators=[
                               RegexValidator(
                                   regex='^[a-zA-Z0-9_\(\)-]+$',
                                   message='Нельзя создать статью по этому пути',
                               ),
                           ],
                           widget=forms.HiddenInput(), label='Адрес')
    comment = forms.CharField(max_length=255,
                              required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control'}), label='Коментарий')
    content = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control article-text', 'rows': 20}),
        label='Статья'
    )


class CommentForm(forms.Form):
    text = forms.CharField(max_length=1000)
