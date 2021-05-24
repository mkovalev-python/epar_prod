# -*- coding:utf-8 -*-
__author__ = 'rayleigh'
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.http import require_http_methods, require_safe, require_POST
from wiking.services.articles import ArticleService
from wiking.views.forms import ArticleForm
from PManager.viewsExt.headers import initGlobals
from PManager.services.projects import get_project_by_id
from django.template import loader, RequestContext


class ArticleView:
    def __init__(self):
        pass

    @staticmethod
    @require_http_methods(['GET', 'POST', 'HEAD'])
    def new(request, project_slug=None):
        project = get_project_by_id(project_slug)
        raw_slug = request.GET.get('slug')
        if not ArticleService.can_create(request.user, project):
            raise PermissionDenied
        if not raw_slug or len(raw_slug) < 1:
            raise Http404
        parent, slug, articles, error = ArticleService.parse_slug(raw_slug, project)
        if error == ArticleService.PATH_NOT_FIND:
            raise Http404
        article = ArticleService.get_article(parent, slug, project)
        if article:
            return HttpResponseRedirect(ArticleService.get_absolute_url(article, articles))
        response = ArticleView.__env(request)
        if request.method == 'POST':
            form = ArticleForm(request.POST)
            response['new_form'] = False
            if form.is_valid():
                data = form.cleaned_data
                data['parent'] = parent
                data['project'] = project
                article = ArticleService.create_article(data, request.user)
                return HttpResponseRedirect(ArticleService.get_absolute_url(article, articles))
        else:
            form = ArticleForm({'slug': slug})
            response['new_form'] = True
        response['form'] = form
        t = loader.get_template('articles/new.html')
        c = RequestContext(request, response)
        return HttpResponse(t.render(c))

    @staticmethod
    @require_http_methods(['GET', 'POST', 'HEAD'])
    def edit(request, article_slug, project_slug=None):
        project = get_project_by_id(project_slug)
        parent, slug, articles, error = ArticleService.parse_slug(article_slug, project)
        article = ArticleService.get_article(parent, slug, project)
        if error == ArticleService.PATH_NOT_FIND:
            raise Http404
        if not ArticleService.can_write(article, request.user):
            raise PermissionDenied
        response = ArticleView.__env(request)
        response['new_form'] = True
        if request.method == 'POST':
            form = ArticleForm(request.POST)
            response['new_form'] = False
            if form.is_valid():
                data = form.cleaned_data
                data['parent'] = parent
                article = ArticleService.update_article(article, data, request.user)
                return HttpResponseRedirect(ArticleService.get_absolute_url(article, articles))
        else:
            form_data = ArticleService.get_form_data(article)
            form = ArticleForm(form_data)
        response['form'] = form
        response['show_url'] = ArticleService.get_absolute_url(article, articles)
        t = loader.get_template('articles/edit.html')
        c = RequestContext(request, response)
        return HttpResponse(t.render(c))

    @staticmethod
    @require_POST
    def delete(request, article_slug, project_slug=None):
        project = get_project_by_id(project_slug)
        parent, slug, articles, error = ArticleService.parse_slug(article_slug, project)
        if error == ArticleService.PATH_NOT_FIND:
            raise Http404
        article = ArticleService.get_article(parent, slug, project)
        if not ArticleService.can_write(article, request.user):
            raise PermissionDenied
        if not article:
            raise Http404
        path = ArticleService.get_parent_path(article, articles)
        article.deleted = True
        article.save()
        return HttpResponseRedirect(path)

    @staticmethod
    @require_safe
    def index(request, project_slug=None):
        response = ArticleView.__env(request)
        project = get_project_by_id(project_slug)
        if project and not request.user.get_profile().hasRole(project):
            raise PermissionDenied
        if project is None:
            response['articles'] = ArticleService.articles(project__isnull=True, level=0, deleted=False)
        else:
            response['articles'] = ArticleService.articles(project__isnull=False, level=0,
                                                           deleted=False, project=project)
        response['project'] = project
        response['can_create'] = ArticleService.can_create(request.user, project)
        t = loader.get_template('articles/index.html')
        c = RequestContext(request, response)
        return HttpResponse(t.render(c))

    @staticmethod
    @require_safe
    def show(request, article_slug, project_slug=None):
        project = get_project_by_id(project_slug)
        parent, slug, articles, error = ArticleService.parse_slug(article_slug, project)
        if error == ArticleService.PATH_NOT_FIND:
            raise Http404
        data = ArticleView.__env(request)
        data['parent'] = parent
        data['breadcrumbs'] = ArticleService.get_breadcrumbs(articles)
        data['project'] = project
        article = ArticleService.get_article(parent, slug, project)
        if not ArticleService.can_read(article, request.user):
            raise PermissionDenied
        data['can_write'] = ArticleService.can_write(article, request.user)
        if not article:
            return HttpResponseRedirect(ArticleService.get_create_path(article_slug, project))
        data['article'] = article
        t = loader.get_template('articles/show.html')
        c = RequestContext(request, data)
        return HttpResponse(t.render(c))

    @staticmethod
    @require_http_methods(['GET', 'HEAD'])
    def revisions(request, article_slug, project_slug=None):
        project = get_project_by_id(project_slug)
        parent, slug, articles, error = ArticleService.parse_slug(article_slug, project)
        if error == ArticleService.PATH_NOT_FIND:
            raise Http404
        data = ArticleView.__env(request)
        data['parent'] = parent
        data['breadcrumbs'] = ArticleService.get_breadcrumbs(articles)
        data['project'] = project
        page = int(request.GET.get('page', 1))
        article = ArticleService.get_article(parent, slug, project)
        if not ArticleService.can_write(article, request.user):
            raise PermissionDenied
        data['article'] = article
        data['article_path'] = ArticleService.get_absolute_url(article, articles)
        data['revisions'] = ArticleService.get_revisions(article, page=page, limit=10)
        data['prev_page'] = None
        if page > 1:
            data['prev_page'] = page - 1
        data['next_page'] = None
        if len(data['revisions']) == 10:
            data['next_page'] = page + 1
        t = loader.get_template('articles/revisions.html')
        c = RequestContext(request, data)
        return HttpResponse(t.render(c))

    @staticmethod
    @require_POST
    def set_revision(request, article_slug, project_slug=None):
        project = get_project_by_id(project_slug)
        parent, slug, articles, error = ArticleService.parse_slug(article_slug, project)
        if error == ArticleService.PATH_NOT_FIND:
            raise Http404
        article = ArticleService.get_article(parent, slug, project)
        if not article:
            raise Http404
        if not ArticleService.can_write(article, request.user):
            raise PermissionDenied
        revision_id = int(request.POST.get('revision_id'))
        success = ArticleService.jump_to_revision(article, revision_id, request.user)
        if success:
            return HttpResponseRedirect(ArticleService.get_absolute_url(article, articles))
        else:
            raise PermissionDenied

    @staticmethod
    def __env(request):
        data = dict()
        data['user'] = request.user
        data['main'] = initGlobals(request)
        return data
