# -*- coding: utf-8 -*-


def transliterate(string):
    letters = {u'ё': u'yo',
               u'й': u'i',
               u'ц': u'ts',
               u'у': u'u',
               u'к': u'k',
               u'е': u'e',
               u'н': u'n',
               u'г': u'g',
               u'ш': u'sh',
               u'щ': u'sch',
               u'з': u'z',
               u'х': u'h',
               u'ъ': u'_',
               u'ф': u'f',
               u'ы': u'i',
               u'в': u'v',
               u'а': u'a',
               u'п': u'p',
               u'р': u'r',
               u'о': u'o',
               u'л': u'l',
               u'д': u'd',
               u'ж': u'zh',
               u'э': u'e',
               u'я': u'ya',
               u'ч': u'ch',
               u'с': u's',
               u'м': u'm',
               u'и': u'i',
               u'т': u't',
               u'ь': u'_',
               u'б': u'b',
               u'ю': u'yu'}
    alphabet = 'qwertyuiopasdfghjklzxcvbnm1234567890'
    string = string.lower()
    for letter, letter_translit in letters.iteritems():
        string = string.replace(letter, letter_translit)

    for c in string:
        if(c not in alphabet):
            string = string.replace(c, '_')

    return string
