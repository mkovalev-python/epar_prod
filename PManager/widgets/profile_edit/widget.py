# -*- coding:utf-8 -*-
from PManager.forms import ProfileForm, SuperUserProfileForm
from PManager.models import PM_Timer
from django.contrib.auth.models import User
from django import forms
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
__author__ = 'Gvammer'


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


def validate_password(password):
    """
    Check the password to be valid against the following rules:
        * Must be 8+ of length
        * Must contain digits (at least one)
        * Must contain uppercase letters (at least one)
    """
    if len(password) < 8:
        raise ValidationError(u"Пароль должен содержать 8 или более символов")
    for symbol in password:
        if symbol.isdigit():
            break
    else:
        raise ValidationError(u"Пароль должен содержать как минимум 1 цифру")
    for symbol in password:
        if symbol.isupper():
            break
    else:
        raise ValidationError(u"Пароль должен содержать как минимум 1 заглавную букву")


def widget(request, headerValues, ar, qargs):
    if request.user.is_superuser:
        profile_form = SuperUserProfileForm
    else:
        profile_form = ProfileForm
    uid = request.GET.get('id', None)
    if uid and request.user.is_staff:
        user = User.objects.get(pk=uid)
    else:
        user = request.user

    if request.user.id != user.id and not request.user.is_superuser:
        return {}

    profile = user.get_profile()

    c = RequestContext(request, processors=[csrf])

    # If the form has been submitted...
    if request.method == 'POST':

        # A form bound to the POST data
        form = profile_form(
            instance=profile,
            data=request.POST,
            files=request.FILES
        )
        # A form bound to the POST data
        user_form = UserForm(instance=user, data=request.POST, files=request.FILES)
        # All validation rules pass
        if form.is_valid() and user_form.is_valid():
            form.save()
            user_form.save()

            password = request.POST.get('new_password', None)

            if password:
                validate_password(password)
                password_confirm = request.POST.get('new_password_confirm', None)
                if password_confirm == password:
                    user.set_password(password)
                    user.save()

            return {'redirect': '/profile/edit/?id='+str(uid)}
    else:
        form = profile_form(instance=profile)
        user_form = UserForm(instance=user)

    try:
        if profile.avatar:
            profile.avatar = str(profile.avatar).replace('PManager', '')

        timers = PM_Timer.objects.raw(
            'SELECT SUM(`seconds`) as summ, id, user_id from PManager_pm_timer WHERE `user_id`=' + str(int(user.id)))
        sum = 0
        if timers:
            for timer in timers:
                if timer.summ:
                    sum += float("%.2f" % (float(timer.summ) / 3600))

        setattr(
            profile,
            'sp',
            {
                'summ': sum,
                'rest': sum * int(profile.sp_price) if profile.sp_price else 0
            }
        )

    except User.DoesNotExist:
        pass

    return {
        'c': c,
        'user': user,
        'profile': profile,
        'form': form,
        'uform': user_form,
        'title': u'Редактирование профиля'
    }
