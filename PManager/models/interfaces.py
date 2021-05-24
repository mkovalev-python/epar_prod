# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from django.db import models


class AccessInterface(models.Model):
    protocol_choices = (
        ('http', 'HTTP'),
        ('ssh', 'SSH'),
        ('ftp', 'FTP'),
        ('rdp', 'RDP'),
        ('mysql', 'MySQL'),
    )
    name = models.CharField(max_length=200, verbose_name=u'Название')
    address = models.CharField(max_length=200, verbose_name=u'Адрес')
    port = models.IntegerField(blank=True, null=True, verbose_name=u'Порт')
    protocol = models.CharField(max_length=10, verbose_name=u'Протокол', choices=protocol_choices)
    username = models.CharField(max_length=40, null=True, blank=True, verbose_name=u'Имя пользователя')
    password = models.CharField(max_length=40, null=True, blank=True, verbose_name=u'Пароль')
    access_roles = models.ManyToManyField('PM_Role', null=True, blank=True,
                                          related_name='file_categories', verbose_name=u'Разрешен доступ')
    project = models.ForeignKey('PM_Project', verbose_name=u'Проект')
    is_git = models.BooleanField(blank=False,verbose_name=u'Локальный гит репозиторий')
    check_flag = None

    @classmethod
    def create_git_interface(cls, project):
        interface = cls(
            name=u'Репозиторий',
            address=project.repository,
            protocol='ssh',
            is_git=True,
            project=project
            )
        interface.save()
        return interface

    @classmethod
    def create_mysql_interface(cls, password, project, host):
        interface = cls(
            name=u'База данных Тестового сервера',
            address=host,
            protocol='mysql',
            is_git=False,
            project=project,
            username=project.repository,
            password=password
        )
        interface.save()
        return interface

    def check(self):
        if self.check_flag != None:
            return self.check_flag

        import ftplib, ping, socket
        if self.protocol == 'ftp':
            try:
                if self.port:
                    ftplib.FTP_PORT = self.port

                ftp = ftplib.FTP(self.address, self.username, self.password, False, 4)
                ftp.voidcmd('NOOP')
                self.check_flag = True
            except Exception:
                self.check_flag = False
        else:
            try:
                # ping.do_one(self.address, 1000, 32)
                self.check_flag = True
            except socket.error, e:
                self.check_flag = False

        return self.check_flag

    class Meta:
        app_label = 'PManager'
