# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Article.head'
        db.alter_column(u'wiking_article', 'head_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['wiking.ArticleVersion']))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Article.head'
        raise RuntimeError("Cannot reverse this migration. 'Article.head' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Article.head'
        db.alter_column(u'wiking_article', 'head_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wiking.ArticleVersion']))

    models = {
        'PManager.pm_project': {
            'Meta': {'object_name': 'PM_Project'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'createdProjects'", 'to': u"orm['auth.User']"}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'dateCreate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repository': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'settings': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'tracker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projects'", 'to': "orm['PManager.PM_Tracker']"})
        },
        'PManager.pm_tracker': {
            'Meta': {'object_name': 'PM_Tracker'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'createdTrackers'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'dateCreate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'wiking.article': {
            'Meta': {'object_name': 'Article'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'head': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'head_article'", 'null': 'True', 'to': "orm['wiking.ArticleVersion']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_articles'", 'to': u"orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['wiking.Article']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wiki_articles'", 'null': 'True', 'to': "orm['PManager.PM_Project']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'wiking.articleversion': {
            'Meta': {'object_name': 'ArticleVersion'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wiking.Article']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        'wiking.comment': {
            'Meta': {'object_name': 'Comment'},
            'article_version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['wiking.ArticleVersion']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['wiking']