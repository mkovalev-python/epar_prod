# coding=utf-8
__author__ = 'Gvammer'
from django import forms
from django.http import HttpResponse
from django.template import RequestContext, loader
from PManager.viewsExt.tools import EmailMessage
from tracker.settings import FEEDBACK_EMAIL
import datetime


class WhoAreYou(forms.Form):
    name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=255, required=False)
    sitename = forms.CharField(max_length=255, required=False)
    need_manager = forms.CharField(max_length=1, required=False)


class Feedback(forms.Form):

    subject = forms.CharField(required=False, max_length=255, label='subject',
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'Ввведите тему'}))
    phone = forms.CharField(required=False, max_length=255, label='phone',
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'Ввведите номер телефона'}))
    name = forms.CharField(required=False, max_length=255, label='name',
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'Ввведите имя'}))
    email = forms.CharField(required=False, max_length=255, label='email',
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'Ввведите email'}))
    message = forms.CharField(max_length=1500, label='message',
                              widget=forms.Textarea(attrs={'class': 'form-control',
                                                           'placeholder': u'Введите сообщение',
                                                           'rows': 2}))


def sendFeedBackEmail(fullName, emailFrom, subject, message):
    mes = {
        'fromUser': fullName,
        'userEmail': emailFrom,
        'subject': subject,
        'message': message,
        'date': datetime.datetime.now()
    }
    sendMes = EmailMessage('feedback', mes, 'New feedback')
    sendMes.send([FEEDBACK_EMAIL])  # if error, admin will know and will resend


def sendFeedback(request):
    form = Feedback(request.POST or None)
    context = {'form': form}

    if 'message' in request.POST and form.is_valid():
        context['send'] = True
        bAuth = request.user.is_authenticated()
        sendFeedBackEmail(
            request.user.first_name + ' ' + request.user.last_name if bAuth else form.cleaned_data['name'],
            request.user.email if bAuth else form.cleaned_data['email'],
            form.cleaned_data['subject'] + ' ' + form.cleaned_data['phone'],
            form.cleaned_data['message']
        )

    c = RequestContext(request, context)
    t = loader.get_template('helpers/feedback.html')
    return HttpResponse(t.render(c))
