# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PM_Project.id_md5'
        db.add_column(u'PManager_pm_project', 'id_md5',
                      self.gf('django.db.models.fields.CharField')(max_length=32, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PM_Project.id_md5'
        db.delete_column(u'PManager_pm_project', 'id_md5')


    models = {
        'PManager.accessinterface': {
            'Meta': {'object_name': 'AccessInterface'},
            'access_roles': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'file_categories'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['PManager.PM_Role']"}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_git': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Project']"}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        'PManager.agent': {
            'Meta': {'object_name': 'Agent'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_process_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_result_message': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'once': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'required': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'seconds': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'PManager.agreement': {
            'Meta': {'object_name': 'Agreement'},
            'approvedByPayer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approvedByResp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'datePayerApprove': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateRespApprove': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jsonData': ('django.db.models.fields.TextField', [], {}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payer_agreements'", 'to': u"orm['auth.User']"}),
            'resp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resp_agreements'", 'to': u"orm['auth.User']"})
        },
        'PManager.conditions': {
            'Meta': {'object_name': 'Conditions'},
            'condition': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'PManager.credit': {
            'Meta': {'object_name': 'Credit'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'credits'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'credits'", 'null': 'True', 'to': "orm['PManager.PM_Project']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'costs'", 'null': 'True', 'to': "orm['PManager.PM_Task']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'arrears'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'PManager.fee': {
            'Meta': {'object_name': 'Fee'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fee'", 'null': 'True', 'to': "orm['PManager.PM_Project']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fee'", 'null': 'True', 'to': "orm['PManager.PM_Task']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fee'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'PManager.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'demo_value': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_time': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'notes_communications': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'notes_do': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'notes_quality': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'notes_was': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Project']"}),
            'quality': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'rating': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'speed': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'standup': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'PManager.finehistory': {
            'Meta': {'object_name': 'FineHistory'},
            'dateCreate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'})
        },
        'PManager.integration': {
            'Meta': {'object_name': 'Integration'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastSendDate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Project']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'PManager.key': {
            'Meta': {'object_name': 'Key'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_data': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'PManager.logdata': {
            'Meta': {'object_name': 'LogData'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'PManager.objecttags': {
            'Meta': {'object_name': 'ObjectTags'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'objectLinks'", 'to': "orm['PManager.Tags']"}),
            'weight': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'PManager.paymentrequest': {
            'Meta': {'object_name': 'PaymentRequest'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'payment_requests'", 'null': 'True', 'to': "orm['PManager.PM_Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'payment_requests'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'PManager.pm_achievement': {
            'Meta': {'object_name': 'PM_Achievement'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'condition': ('django.db.models.fields.TextField', [], {}),
            'delete_on_first_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'use_in_projects': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'PManager.pm_file_category': {
            'Meta': {'object_name': 'PM_File_Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['PManager.PM_File_Category']"}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'file_categories'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['PManager.PM_Project']"})
        },
        'PManager.pm_files': {
            'Meta': {'object_name': 'PM_Files'},
            'authorId': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'files'", 'null': 'True', 'to': "orm['PManager.PM_File_Category']"}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '400'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_old_version': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'projectId': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Project']", 'null': 'True'}),
            'versions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'versions_rel_+'", 'null': 'True', 'to': "orm['PManager.PM_Files']"})
        },
        'PManager.pm_holidays': {
            'Meta': {'object_name': 'PM_Holidays'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'PManager.pm_milestone': {
            'Meta': {'object_name': 'PM_Milestone'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'criteria': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'critically': ('django.db.models.fields.IntegerField', [], {'default': '2', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2020, 6, 2, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'delay_deduction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'extra_hours': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fact_close_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_md5': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'milestones'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'overdue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'milestones'", 'to': "orm['PManager.PM_Project']"}),
            'responsible': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '25', 'null': 'True', 'blank': 'True'})
        },
        'PManager.pm_milestonechanges': {
            'Meta': {'object_name': 'PM_MilestoneChanges'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changes'", 'to': "orm['PManager.PM_Milestone']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'PManager.pm_milestonestatus': {
            'Meta': {'object_name': 'PM_MilestoneStatus'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'createdSpints'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sprint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statuses'", 'to': "orm['PManager.PM_Milestone']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'})
        },
        'PManager.pm_notice': {
            'Meta': {'object_name': 'PM_Notice'},
            'html': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'itemClass': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'PManager.pm_noticedusers': {
            'Meta': {'object_name': 'PM_NoticedUsers'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2020, 6, 2, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'userNotices'", 'to': "orm['PManager.PM_Notice']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notices'", 'to': u"orm['auth.User']"})
        },
        'PManager.pm_project': {
            'Meta': {'ordering': "('name',)", 'object_name': 'PM_Project'},
            'api_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'createdProjects'", 'to': u"orm['auth.User']"}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'dateCreate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_md5': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'repository': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'settings': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'tracker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projects'", 'to': "orm['PManager.PM_Tracker']"})
        },
        'PManager.pm_project_achievement': {
            'Meta': {'object_name': 'PM_Project_Achievement'},
            'achievement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Achievement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'once_per_project': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Project']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'fix'", 'max_length': '100'}),
            'value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'PManager.pm_projectroles': {
            'Meta': {'object_name': 'PM_ProjectRoles'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_type': ('django.db.models.fields.CharField', [], {'default': "'real_time'", 'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projectRoles'", 'to': "orm['PManager.PM_Project']"}),
            'rate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'userRoles'", 'to': u"orm['auth.User']"})
        },
        'PManager.pm_properties': {
            'Meta': {'object_name': 'PM_Properties'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'PManager.pm_property_values': {
            'Meta': {'object_name': 'PM_Property_Values'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'propertyId': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Properties']"}),
            'taskId': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Task']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'PManager.pm_reminder': {
            'Meta': {'object_name': 'PM_Reminder'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Task']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'PManager.pm_role': {
            'Meta': {'object_name': 'PM_Role'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'tracker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Tracker']"})
        },
        'PManager.pm_task': {
            'Meta': {'object_name': 'PM_Task'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'createdTasks'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'closedInTime': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'color': ('django.db.models.fields.CharField', [], {'default': "'blue'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'critically': ('django.db.models.fields.FloatField', [], {'default': '0.5'}),
            'dateClose': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateCreate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dateModify': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'dateStart': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'fileTasks'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['PManager.PM_Files']"}),
            'hardness': ('django.db.models.fields.FloatField', [], {'default': '0.5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isParent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lastModifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'modifiedBy'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasks'", 'null': 'True', 'to': "orm['PManager.PM_Milestone']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'observers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tasksLooking'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'onPlanning': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parentTask': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subTasks'", 'null': 'True', 'to': "orm['PManager.PM_Task']"}),
            'perhapsResponsible': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'hisTasksMaybe'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'planTime': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.FloatField', [], {'default': '0.5'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'projectTasks'", 'null': 'True', 'to': "orm['PManager.PM_Project']"}),
            'project_knowledge': ('django.db.models.fields.FloatField', [], {'default': '0.5'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'realDateStart': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'realTime': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reconcilement': ('django.db.models.fields.FloatField', [], {'default': '0.5'}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasks'", 'null': 'True', 'to': "orm['PManager.Release']"}),
            'repeatEvery': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'resp': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'todo'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'responsible': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'hisTasks'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tasksByStatus'", 'null': 'True', 'to': "orm['PManager.PM_Task_Status']"}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'viewedUsers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'virgin': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wasClosed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'PManager.pm_task_message': {
            'Meta': {'object_name': 'PM_Task_Message'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'outputMessages'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'bug': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'checked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '42', 'null': 'True', 'blank': 'True'}),
            'dateCreate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dateModify': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'msgTasks'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['PManager.PM_Files']"}),
            'filesExist': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hidden_from_clients': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hidden_from_employee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isSystemLog': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Project']", 'null': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'requested_time_approve_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'requested_time_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested_time_approved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'approvedTimeRequests'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'solution': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'null': 'True', 'to': "orm['PManager.PM_Task']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'todo': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'userTo': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'incomingMessages'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'PManager.pm_task_status': {
            'Meta': {'object_name': 'PM_Task_Status'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'PManager.pm_timer': {
            'Meta': {'object_name': 'PM_Timer'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'dateEnd': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dateStart': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'seconds': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Task']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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
        'PManager.pm_user': {
            'Meta': {'object_name': 'PM_User'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'avatar_color': ('django.db.models.fields.CharField', [], {'default': "'#008080'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'bank': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'bik': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'documentIssueDate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'documentIssuedBy': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'documentNumber': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'heliard_manager_rate': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'hoursQtyPerDay': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'icq': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_heliard_manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_outsource': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': "'ru'", 'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'last_activity_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'overdraft': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'paid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'phoneNumber': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'premium_till': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'second_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'skype': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'sp_price': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'specialties': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'profiles'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['PManager.Specialty']"}),
            'specialty': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.Specialty']", 'null': 'True', 'blank': 'True'}),
            'trackers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['PManager.PM_Tracker']", 'null': 'True', 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        'PManager.pm_user_achievement': {
            'Meta': {'object_name': 'PM_User_Achievement'},
            'achievement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'achievement_users'", 'to': "orm['PManager.PM_Achievement']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Project']", 'null': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_achievements'", 'to': u"orm['auth.User']"})
        },
        'PManager.pm_user_plantime': {
            'Meta': {'object_name': 'PM_User_PlanTime'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Task']"}),
            'time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'PManager.ratinghistory': {
            'Meta': {'object_name': 'RatingHistory'},
            'dateCreate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'})
        },
        'PManager.release': {
            'Meta': {'object_name': 'Release'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['PManager.PM_Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '30'})
        },
        'PManager.simplemessage': {
            'Meta': {'object_name': 'SimpleMessage'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'simple_messages'", 'to': u"orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Task']"}),
            'task_draft': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.TaskDraft']"}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '10000'})
        },
        'PManager.slackintegration': {
            'Meta': {'object_name': 'SlackIntegration', '_ormbases': ['PManager.Integration']},
            u'integration_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['PManager.Integration']", 'unique': 'True', 'primary_key': 'True'})
        },
        'PManager.specialty': {
            'Meta': {'object_name': 'Specialty'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'PManager.tags': {
            'Meta': {'object_name': 'Tags'},
            'frequency': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tagText': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'PManager.taskdraft': {
            'Meta': {'object_name': 'TaskDraft'},
            '_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'status'", 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'task_drafts'", 'to': u"orm['auth.User']"}),
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'task_drafts'", 'null': 'True', 'to': "orm['PManager.PM_Project']"}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'specialties': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['PManager.Specialty']", 'symmetrical': 'False', 'blank': 'True'}),
            'tasks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['PManager.PM_Task']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'PManager.test': {
            'Meta': {'object_name': 'Test'},
            'condition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.Conditions']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'passed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tests'", 'to': "orm['PManager.PM_Project']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['PManager']