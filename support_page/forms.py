# -*- coding:utf-8 -*-
from django import forms


class SupportForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input JSplaceholderAppdate', 'placeholder': u'Имя'}))
    phone = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class': 'input _area JSplaceholderAppdate', 'placeholder': u'Контакты, Доступы'}))
    priority = forms.BooleanField(label=u'Блокирующий приоритет', required=False, widget=forms.CheckboxInput(attrs={'class': 'formBox__confirmInput'}))
    link = forms.CharField(max_length=512, widget=forms.TextInput(attrs={'class': 'input JSplaceholderAppdate', 'placeholder': u'Ссылка на страницу по которой ставится задача'}))
    screenshot = forms.FileField(label=u'Скриншот ошибки', required=False, widget=forms.FileInput(attrs={'class': 'input-file'}))
    work_actual = forms.CharField(widget=forms.Textarea(attrs={'class': 'input _area JSplaceholderAppdate', 'placeholder': u'Как сейчас это работает в системе'}))
    work_should = forms.CharField(widget=forms.Textarea(attrs={'class': 'input _area JSplaceholderAppdate', 'placeholder': u'Как должно работать'}))
    details = forms.CharField(widget=forms.Textarea(attrs={'class': 'input _area JSplaceholderAppdate', 'placeholder': u'Дополнительно'}))

    def __init__(self, *args, **kwargs):
        super(SupportForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs["required"] = "required"
        self.fields['phone'].widget.attrs["required"] = "required"
        self.fields['link'].widget.attrs["required"] = "required"
        self.fields['work_actual'].widget.attrs["required"] = "required"
        self.fields['work_should'].widget.attrs["required"] = "required"
