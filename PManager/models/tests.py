# coding=utf-8
__author__ = 'Alwx'

from django.db import models
from PManager.models.tasks import PM_Project


class Conditions(models.Model):
    field_choices = (
        ('Header', u'Заголовок'),
        ('Body', u'Тело')
    )

    field = models.CharField(max_length=15, choices=field_choices, verbose_name=u'Поле', blank=True, null=True)
    condition = models.BooleanField(verbose_name=u'Содержит')
    value = models.CharField(max_length=255, verbose_name=u'Значение', blank=True, null=True)

    def __unicode__(self):
        return ' '.join([self.get_field_display(), self.get_condition_display(), self.value])

    class Meta:
        app_label = 'PManager'


class Test(models.Model):
    project = models.ForeignKey(PM_Project, related_name='tests', verbose_name=u'Проект')
    condition = models.ForeignKey(Conditions, verbose_name=u'Условие')
    passed = models.BooleanField(blank=True, verbose_name=u'Пройден')
    url = models.CharField(max_length=255, blank=True, null=True)

    def test(self):
        new_test = RunTest(self.url, self.condition.field, self.condition.condition, self.condition.value)
        return new_test.passed()

    class Meta:
        app_label = 'PManager'

class RunTest:

    def __init__(self, url, field, condition, value):
        self.url = url
        self.field = field
        self.condition = condition
        self.value = value

    def passed(self):
        result = False

        if self.field == 'Header':
            result = self.header()
        elif self.field == 'Body':
            result = self.body()

        return result

    def header(self):
        return False

    def body(self):
        from selenium import webdriver
        from bs4 import BeautifulSoup
        import re

        driver = webdriver.Firefox()
        driver.get(self.url)
        soup = BeautifulSoup(driver.page_source)
        driver.quit()

        if re.search('^/*/', self.value):
            result = soup(text=re.compile(self.value))  # TODO Разобраться в каком виде будет строка с регуляркой
        else:
            result = soup.select(self.value)

        if not self.condition:
            result = not result

        if result:
            return True
        else:
            return False
