# -*- coding:utf-8 -*-
from django.template import Library

register = Library()


def get_ending(number, words):
    try:
        number = int(number)
    except ValueError:
        word = words[3]
    else:
        t = number % 100
        if 11 <= t <= 19:
            word = words[2]
        else:
            i = t % 10
            if i == 1:
                word = words[0]
            elif 2 <= i <= 4:
                word = words[1]
            else:
                word = words[2]
    return u'{} {}'.format(number, word)


@register.simple_tag(name='get_hours_ending')
def get_hours_ending(number):
    words = [u'час', u'часа', u'часов', u'час(-а)(-ов)']
    return get_ending(number, words)


@register.simple_tag(name='get_days_ending')
def get_days_ending(number):
    words = [u'день', u'дня', u'дней', u'день(-я)(-ей)']
    return get_ending(number, words)
