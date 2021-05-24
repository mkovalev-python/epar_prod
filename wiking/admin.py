__author__ = 'Gvammer'
from django.contrib import admin
from wiking.models import Article, ArticleVersion

admin.site.register(Article)
admin.site.register(ArticleVersion)