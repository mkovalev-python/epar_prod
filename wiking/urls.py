__author__ = 'rayleigh'

from django.conf.urls import *
from views import ArticleView
urlpatterns = patterns('wiking.views',
   (r'^project/(?P<project_slug>[0-9_]+)/$', ArticleView.index),
   (r'^project/(?P<project_slug>[0-9_]+)/new$', ArticleView.new),
   (r'^project/(?P<project_slug>[0-9_]+)/(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/edit$', ArticleView.edit),
   (r'^project/(?P<project_slug>[0-9_]+)/(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/delete$', ArticleView.delete),
   (r'^project/(?P<project_slug>[0-9_]+)/(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/revisions$', ArticleView.revisions),
   (r'^project/(?P<project_slug>[0-9_]+)/(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/set_revision', ArticleView.set_revision),
   (r'^project/(?P<project_slug>[0-9_]+)/(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/$', ArticleView.show),
   (r'^project/(?P<project_slug>[0-9_]+)/$', ArticleView.index),
   (r'^new$', ArticleView.new),
   (r'^(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/edit$', ArticleView.edit),
   (r'^(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/delete$', ArticleView.delete),
   (r'^(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/revisions$', ArticleView.revisions),
   (r'^(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/set_revision$', ArticleView.set_revision),
   (r'^(?P<article_slug>[a-zA-Z0-9_\(\)-/]+)/$', ArticleView.show),
   (r'^$', ArticleView.index),
)

