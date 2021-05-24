# -*- coding:utf-8 -*-
from django import forms

from PManager.models import PM_User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = PM_User
        fields = (
            'second_name',
            'phoneNumber',
            'skype',
            'telegram',
            'avatar',
            'hoursQtyPerDay',
        )

    def clean_telegram(self):
        telegram = self.cleaned_data.get('telegram', None)
        if telegram:
            pm_user = PM_User.objects.filter(telegram=telegram)
            if pm_user and pm_user[0] != self.instance:
                raise forms.ValidationError(u'Такой пользователь Telegram уже есть')
        return telegram


class SuperUserProfileForm(ProfileForm):
    class Meta(ProfileForm.Meta):
        fields = ProfileForm.Meta.fields + ('specialties', 'sp_price', 'overdraft')
