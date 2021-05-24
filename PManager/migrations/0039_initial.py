# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tags'
        db.create_table(u'PManager_tags', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tagText', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('frequency', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('PManager', ['Tags'])

        # Adding model 'ObjectTags'
        db.create_table(u'PManager_objecttags', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='objectLinks', to=orm['PManager.Tags'])),
            ('weight', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('PManager', ['ObjectTags'])

        # Adding model 'PM_Tracker'
        db.create_table(u'PManager_pm_tracker', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dateCreate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('admin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='createdTrackers', null=True, to=orm['auth.User'])),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
        ))
        db.send_create_signal('PManager', ['PM_Tracker'])

        # Adding model 'PM_Project'
        db.create_table(u'PManager_pm_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_md5', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('dateCreate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='createdProjects', to=orm['auth.User'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('tracker', self.gf('django.db.models.fields.related.ForeignKey')(related_name='projects', to=orm['PManager.PM_Tracker'])),
            ('repository', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('api_key', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('settings', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('PManager', ['PM_Project'])

        # Adding model 'Release'
        db.create_table(u'PManager_release', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=30)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='releases', to=orm['PManager.PM_Project'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('PManager', ['Release'])

        # Adding model 'PM_File_Category'
        db.create_table(u'PManager_pm_file_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['PManager.PM_File_Category'])),
        ))
        db.send_create_signal('PManager', ['PM_File_Category'])

        # Adding M2M table for field projects on 'PM_File_Category'
        m2m_table_name = db.shorten_name(u'PManager_pm_file_category_projects')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_file_category', models.ForeignKey(orm['PManager.pm_file_category'], null=False)),
            ('pm_project', models.ForeignKey(orm['PManager.pm_project'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_file_category_id', 'pm_project_id'])

        # Adding model 'PM_Files'
        db.create_table(u'PManager_pm_files', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=400)),
            ('authorId', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('projectId', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Project'], null=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='files', null=True, to=orm['PManager.PM_File_Category'])),
            ('is_old_version', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('date_create', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('double', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attach', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('PManager', ['PM_Files'])

        # Adding M2M table for field versions on 'PM_Files'
        m2m_table_name = db.shorten_name(u'PManager_pm_files_versions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_pm_files', models.ForeignKey(orm['PManager.pm_files'], null=False)),
            ('to_pm_files', models.ForeignKey(orm['PManager.pm_files'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_pm_files_id', 'to_pm_files_id'])

        # Adding model 'PM_Task_Status'
        db.create_table(u'PManager_pm_task_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('PManager', ['PM_Task_Status'])

        # Adding model 'PM_Milestone'
        db.create_table(u'PManager_pm_milestone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('id_md5', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.CharField')(default='', max_length=4000, null=True, blank=True)),
            ('target', self.gf('django.db.models.fields.CharField')(default='', max_length=4000, null=True, blank=True)),
            ('criteria', self.gf('django.db.models.fields.CharField')(default='', max_length=4000, null=True, blank=True)),
            ('file_for_client', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_create', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('critically', self.gf('django.db.models.fields.IntegerField')(default=2, null=True, blank=True)),
            ('extra_hours', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='milestones', to=orm['PManager.PM_Project'])),
            ('overdue', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delay_deduction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('final_delay', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='milestones', null=True, to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.CharField')(default=0, max_length=25, null=True, db_index=True, blank=True)),
            ('fact_close_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_close_confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_half_completed', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('is_has_grooming', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('delay_factor', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('g_factor', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('PManager', ['PM_Milestone'])

        # Adding M2M table for field responsible on 'PM_Milestone'
        m2m_table_name = db.shorten_name(u'PManager_pm_milestone_responsible')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_milestone', models.ForeignKey(orm['PManager.pm_milestone'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_milestone_id', 'user_id'])

        # Adding model 'PM_MilestoneStatus'
        db.create_table(u'PManager_pm_milestonestatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sprint', self.gf('django.db.models.fields.related.ForeignKey')(related_name='statuses', to=orm['PManager.PM_Milestone'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='createdSpints', null=True, to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=15, db_index=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_create', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PM_MilestoneStatus'])

        # Adding model 'PM_MilestoneDevPaymentApproval'
        db.create_table(u'PManager_pm_milestonedevpaymentapproval', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Milestone'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_approved', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PM_MilestoneDevPaymentApproval'])

        # Adding unique constraint on 'PM_MilestoneDevPaymentApproval', fields ['milestone', 'user']
        db.create_unique(u'PManager_pm_milestonedevpaymentapproval', ['milestone_id', 'user_id'])

        # Adding model 'PM_Task'
        db.create_table(u'PManager_pm_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('text_ro', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('text_eo', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='projectTasks', null=True, to=orm['PManager.PM_Project'])),
            ('resp', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='todo', null=True, to=orm['auth.User'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='createdTasks', null=True, to=orm['auth.User'])),
            ('lastModifiedBy', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='modifiedBy', null=True, to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tasksByStatus', null=True, to=orm['PManager.PM_Task_Status'])),
            ('dateCreate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('dateModify', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('dateClose', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dateStart', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tasks', null=True, to=orm['PManager.PM_Milestone'])),
            ('onPlanning', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('planTime', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('planTimeMainOrg', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('planTimeRegulator', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('realTime', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('realDateStart', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('started', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wasClosed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('closedInTime', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('priority', self.gf('django.db.models.fields.FloatField')(default=0.5)),
            ('critically', self.gf('django.db.models.fields.FloatField')(default=0.5)),
            ('hardness', self.gf('django.db.models.fields.FloatField')(default=0.5)),
            ('reconcilement', self.gf('django.db.models.fields.FloatField')(default=0.5)),
            ('project_knowledge', self.gf('django.db.models.fields.FloatField')(default=0.5)),
            ('parentTask', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subTasks', null=True, to=orm['PManager.PM_Task'])),
            ('virgin', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('repeatEvery', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(default='blue', max_length=100, null=True, blank=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tasks', null=True, to=orm['PManager.Release'])),
            ('isParent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.related.OneToOneField')(related_name='category', null=True, on_delete=models.SET_NULL, to=orm['PManager.PM_File_Category'], blank=True, unique=True)),
        ))
        db.send_create_signal('PManager', ['PM_Task'])

        # Adding M2M table for field responsible on 'PM_Task'
        m2m_table_name = db.shorten_name(u'PManager_pm_task_responsible')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_task', models.ForeignKey(orm['PManager.pm_task'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_task_id', 'user_id'])

        # Adding M2M table for field observers on 'PM_Task'
        m2m_table_name = db.shorten_name(u'PManager_pm_task_observers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_task', models.ForeignKey(orm['PManager.pm_task'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_task_id', 'user_id'])

        # Adding M2M table for field perhapsResponsible on 'PM_Task'
        m2m_table_name = db.shorten_name(u'PManager_pm_task_perhapsResponsible')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_task', models.ForeignKey(orm['PManager.pm_task'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_task_id', 'user_id'])

        # Adding M2M table for field viewedUsers on 'PM_Task'
        m2m_table_name = db.shorten_name(u'PManager_pm_task_viewedUsers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_task', models.ForeignKey(orm['PManager.pm_task'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_task_id', 'user_id'])

        # Adding M2M table for field files on 'PM_Task'
        m2m_table_name = db.shorten_name(u'PManager_pm_task_files')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_task', models.ForeignKey(orm['PManager.pm_task'], null=False)),
            ('pm_files', models.ForeignKey(orm['PManager.pm_files'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_task_id', 'pm_files_id'])

        # Adding M2M table for field files_ro on 'PM_Task'
        m2m_table_name = db.shorten_name(u'PManager_pm_task_files_ro')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_task', models.ForeignKey(orm['PManager.pm_task'], null=False)),
            ('pm_files', models.ForeignKey(orm['PManager.pm_files'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_task_id', 'pm_files_id'])

        # Adding M2M table for field files_eo on 'PM_Task'
        m2m_table_name = db.shorten_name(u'PManager_pm_task_files_eo')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_task', models.ForeignKey(orm['PManager.pm_task'], null=False)),
            ('pm_files', models.ForeignKey(orm['PManager.pm_files'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_task_id', 'pm_files_id'])

        # Adding model 'PM_Timer'
        db.create_table(u'PManager_pm_timer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Task'])),
            ('dateStart', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('dateEnd', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('seconds', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('price', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PM_Timer'])

        # Adding model 'PM_Properties'
        db.create_table(u'PManager_pm_properties', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('PManager', ['PM_Properties'])

        # Adding model 'PM_Property_Values'
        db.create_table(u'PManager_pm_property_values', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('propertyId', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Properties'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('taskId', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Task'])),
        ))
        db.send_create_signal('PManager', ['PM_Property_Values'])

        # Adding model 'PM_Task_Message'
        db.create_table(u'PManager_pm_task_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=10000)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='outputMessages', null=True, to=orm['auth.User'])),
            ('dateCreate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('dateModify', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('modifiedBy', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', null=True, to=orm['PManager.PM_Task'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Project'], null=True)),
            ('commit', self.gf('django.db.models.fields.CharField')(max_length=42, null=True, blank=True)),
            ('userTo', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='incomingMessages', null=True, to=orm['auth.User'])),
            ('filesExist', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hidden_from_clients', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hidden_from_employee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('isSystemLog', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('todo', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('checked', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('bug', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('solution', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requested_time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('requested_time_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requested_time_approved_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='approvedTimeRequests', null=True, to=orm['auth.User'])),
            ('requested_time_approve_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PM_Task_Message'])

        # Adding M2M table for field files on 'PM_Task_Message'
        m2m_table_name = db.shorten_name(u'PManager_pm_task_message_files')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_task_message', models.ForeignKey(orm['PManager.pm_task_message'], null=False)),
            ('pm_files', models.ForeignKey(orm['PManager.pm_files'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_task_message_id', 'pm_files_id'])

        # Adding model 'PM_Role'
        db.create_table(u'PManager_pm_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('tracker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Tracker'])),
        ))
        db.send_create_signal('PManager', ['PM_Role'])

        # Adding model 'PM_ProjectRoles'
        db.create_table(u'PManager_pm_projectroles', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='userRoles', to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='projectRoles', to=orm['PManager.PM_Project'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Role'])),
            ('rate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('payment_type', self.gf('django.db.models.fields.CharField')(default='real_time', max_length=100)),
        ))
        db.send_create_signal('PManager', ['PM_ProjectRoles'])

        # Adding model 'PM_User_PlanTime'
        db.create_table(u'PManager_pm_user_plantime', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Task'])),
            ('time', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PM_User_PlanTime'])

        # Adding model 'PM_Reminder'
        db.create_table(u'PManager_pm_reminder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Task'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('PManager', ['PM_Reminder'])

        # Adding model 'PM_Holidays'
        db.create_table(u'PManager_pm_holidays', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('PManager', ['PM_Holidays'])

        # Adding model 'RatingHistory'
        db.create_table(u'PManager_ratinghistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], blank=True)),
            ('dateCreate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['RatingHistory'])

        # Adding model 'FineHistory'
        db.create_table(u'PManager_finehistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], blank=True)),
            ('dateCreate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['FineHistory'])

        # Adding model 'Credit'
        db.create_table(u'PManager_credit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='arrears', null=True, to=orm['auth.User'])),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='credits', null=True, to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='credits', null=True, to=orm['PManager.PM_Project'])),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='credits', null=True, to=orm['PManager.PM_Milestone'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='costs', null=True, to=orm['PManager.PM_Task'])),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(default='0', max_length=32)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['Credit'])

        # Adding model 'PaymentRequest'
        db.create_table(u'PManager_paymentrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='payment_requests', null=True, to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='payment_requests', null=True, to=orm['PManager.PM_Project'])),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PaymentRequest'])

        # Adding model 'Fee'
        db.create_table(u'PManager_fee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fee', null=True, to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fee', null=True, to=orm['PManager.PM_Project'])),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fee', null=True, to=orm['PManager.PM_Task'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['Fee'])

        # Adding model 'PM_Achievement'
        db.create_table(u'PManager_pm_achievement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('condition', self.gf('django.db.models.fields.TextField')()),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('delete_on_first_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('use_in_projects', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('PManager', ['PM_Achievement'])

        # Adding model 'PM_Project_Achievement'
        db.create_table(u'PManager_pm_project_achievement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('achievement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Achievement'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Project'])),
            ('value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='fix', max_length=100)),
            ('once_per_project', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('PManager', ['PM_Project_Achievement'])

        # Adding model 'PM_User_Achievement'
        db.create_table(u'PManager_pm_user_achievement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_achievements', to=orm['auth.User'])),
            ('achievement', self.gf('django.db.models.fields.related.ForeignKey')(related_name='achievement_users', to=orm['PManager.PM_Achievement'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Project'], null=True)),
        ))
        db.send_create_signal('PManager', ['PM_User_Achievement'])

        # Adding model 'Specialty'
        db.create_table(u'PManager_specialty', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('PManager', ['Specialty'])

        # Adding model 'PM_User'
        db.create_table(u'PManager_pm_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('second_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('icq', self.gf('django.db.models.fields.CharField')(max_length=70, null=True, blank=True)),
            ('skype', self.gf('django.db.models.fields.CharField')(max_length=70, null=True, blank=True)),
            ('telegram', self.gf('django.db.models.fields.CharField')(max_length=70, null=True, blank=True)),
            ('telegram_id', self.gf('django.db.models.fields.CharField')(max_length=70, null=True, blank=True)),
            ('phoneNumber', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('documentNumber', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('documentIssueDate', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('documentIssuedBy', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('bank', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('bik', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('sp_price', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('premium_till', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('paid', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('specialty', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.Specialty'], null=True, blank=True)),
            ('avatar_color', self.gf('django.db.models.fields.CharField')(default='#DCDCDC', max_length=20, null=True, blank=True)),
            ('last_activity_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_outsource', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_heliard_manager', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('heliard_manager_rate', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('overdraft', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lang', self.gf('django.db.models.fields.CharField')(default='ru', max_length=3, null=True, blank=True)),
            ('hoursQtyPerDay', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PM_User'])

        # Adding M2M table for field trackers on 'PM_User'
        m2m_table_name = db.shorten_name(u'PManager_pm_user_trackers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_user', models.ForeignKey(orm['PManager.pm_user'], null=False)),
            ('pm_tracker', models.ForeignKey(orm['PManager.pm_tracker'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_user_id', 'pm_tracker_id'])

        # Adding M2M table for field specialties on 'PM_User'
        m2m_table_name = db.shorten_name(u'PManager_pm_user_specialties')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pm_user', models.ForeignKey(orm['PManager.pm_user'], null=False)),
            ('specialty', models.ForeignKey(orm['PManager.specialty'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pm_user_id', 'specialty_id'])

        # Adding model 'PMTelegramUser'
        db.create_table(u'PManager_pmtelegramuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='telegram_user', unique=True, null=True, to=orm['auth.User'])),
            ('telegram', self.gf('django.db.models.fields.CharField')(max_length=70, null=True, blank=True)),
            ('telegram_id', self.gf('django.db.models.fields.CharField')(max_length=70, null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PMTelegramUser'])

        # Adding model 'PMUserWorkload'
        db.create_table(u'PManager_pmuserworkload', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='workloads', to=orm['PManager.PMTelegramUser'])),
            ('workload', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PMUserWorkload'])

        # Adding model 'PM_Notice'
        db.create_table(u'PManager_pm_notice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('html', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('itemClass', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('PManager', ['PM_Notice'])

        # Adding model 'PM_NoticedUsers'
        db.create_table(u'PManager_pm_noticedusers', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notices', to=orm['auth.User'])),
            ('notice', self.gf('django.db.models.fields.related.ForeignKey')(related_name='userNotices', to=orm['PManager.PM_Notice'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2021, 5, 24, 0, 0))),
        ))
        db.send_create_signal('PManager', ['PM_NoticedUsers'])

        # Adding model 'Agent'
        db.create_table(u'PManager_agent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('seconds', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('required', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('once', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_result_message', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('last_process_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['Agent'])

        # Adding model 'LogData'
        db.create_table(u'PManager_logdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('project_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['LogData'])

        # Adding model 'AccessInterface'
        db.create_table(u'PManager_accessinterface', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Project'])),
            ('is_git', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('PManager', ['AccessInterface'])

        # Adding M2M table for field access_roles on 'AccessInterface'
        m2m_table_name = db.shorten_name(u'PManager_accessinterface_access_roles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('accessinterface', models.ForeignKey(orm['PManager.accessinterface'], null=False)),
            ('pm_role', models.ForeignKey(orm['PManager.pm_role'], null=False))
        ))
        db.create_unique(m2m_table_name, ['accessinterface_id', 'pm_role_id'])

        # Adding model 'TaskDraft'
        db.create_table(u'PManager_taskdraft', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='task_drafts', to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='task_drafts', null=True, to=orm['PManager.PM_Project'])),
            ('closed_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='status', blank=True)),
        ))
        db.send_create_signal('PManager', ['TaskDraft'])

        # Adding M2M table for field users on 'TaskDraft'
        m2m_table_name = db.shorten_name(u'PManager_taskdraft_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taskdraft', models.ForeignKey(orm['PManager.taskdraft'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taskdraft_id', 'user_id'])

        # Adding M2M table for field tasks on 'TaskDraft'
        m2m_table_name = db.shorten_name(u'PManager_taskdraft_tasks')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taskdraft', models.ForeignKey(orm['PManager.taskdraft'], null=False)),
            ('pm_task', models.ForeignKey(orm['PManager.pm_task'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taskdraft_id', 'pm_task_id'])

        # Adding M2M table for field specialties on 'TaskDraft'
        m2m_table_name = db.shorten_name(u'PManager_taskdraft_specialties')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taskdraft', models.ForeignKey(orm['PManager.taskdraft'], null=False)),
            ('specialty', models.ForeignKey(orm['PManager.specialty'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taskdraft_id', 'specialty_id'])

        # Adding model 'SimpleMessage'
        db.create_table(u'PManager_simplemessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='simple_messages', to=orm['auth.User'])),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=10000)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Task'])),
            ('task_draft', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.TaskDraft'])),
        ))
        db.send_create_signal('PManager', ['SimpleMessage'])

        # Adding model 'Conditions'
        db.create_table(u'PManager_conditions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('condition', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['Conditions'])

        # Adding model 'Test'
        db.create_table(u'PManager_test', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tests', to=orm['PManager.PM_Project'])),
            ('condition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.Conditions'])),
            ('passed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['Test'])

        # Adding model 'Agreement'
        db.create_table(u'PManager_agreement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payer_agreements', to=orm['auth.User'])),
            ('resp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resp_agreements', to=orm['auth.User'])),
            ('jsonData', self.gf('django.db.models.fields.TextField')()),
            ('approvedByPayer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('datePayerApprove', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('approvedByResp', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('dateRespApprove', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['Agreement'])

        # Adding model 'Integration'
        db.create_table(u'PManager_integration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('lastSendDate', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['Integration'])

        # Adding model 'SlackIntegration'
        db.create_table(u'PManager_slackintegration', (
            (u'integration_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['PManager.Integration'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('PManager', ['SlackIntegration'])

        # Adding model 'PM_MilestoneChanges'
        db.create_table(u'PManager_pm_milestonechanges', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('milestone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='changes', to=orm['PManager.PM_Milestone'])),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('PManager', ['PM_MilestoneChanges'])

        # Adding model 'Feedback'
        db.create_table(u'PManager_feedback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['PManager.PM_Project'])),
            ('meeting_time', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('demo_value', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('standup', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('speed', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('quality', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('notes_communications', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('notes_quality', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('rating', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('notes_was', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('notes_do', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
        ))
        db.send_create_signal('PManager', ['Feedback'])


    def backwards(self, orm):
        # Removing unique constraint on 'PM_MilestoneDevPaymentApproval', fields ['milestone', 'user']
        db.delete_unique(u'PManager_pm_milestonedevpaymentapproval', ['milestone_id', 'user_id'])

        # Deleting model 'Tags'
        db.delete_table(u'PManager_tags')

        # Deleting model 'ObjectTags'
        db.delete_table(u'PManager_objecttags')

        # Deleting model 'PM_Tracker'
        db.delete_table(u'PManager_pm_tracker')

        # Deleting model 'PM_Project'
        db.delete_table(u'PManager_pm_project')

        # Deleting model 'Release'
        db.delete_table(u'PManager_release')

        # Deleting model 'PM_File_Category'
        db.delete_table(u'PManager_pm_file_category')

        # Removing M2M table for field projects on 'PM_File_Category'
        db.delete_table(db.shorten_name(u'PManager_pm_file_category_projects'))

        # Deleting model 'PM_Files'
        db.delete_table(u'PManager_pm_files')

        # Removing M2M table for field versions on 'PM_Files'
        db.delete_table(db.shorten_name(u'PManager_pm_files_versions'))

        # Deleting model 'PM_Task_Status'
        db.delete_table(u'PManager_pm_task_status')

        # Deleting model 'PM_Milestone'
        db.delete_table(u'PManager_pm_milestone')

        # Removing M2M table for field responsible on 'PM_Milestone'
        db.delete_table(db.shorten_name(u'PManager_pm_milestone_responsible'))

        # Deleting model 'PM_MilestoneStatus'
        db.delete_table(u'PManager_pm_milestonestatus')

        # Deleting model 'PM_MilestoneDevPaymentApproval'
        db.delete_table(u'PManager_pm_milestonedevpaymentapproval')

        # Deleting model 'PM_Task'
        db.delete_table(u'PManager_pm_task')

        # Removing M2M table for field responsible on 'PM_Task'
        db.delete_table(db.shorten_name(u'PManager_pm_task_responsible'))

        # Removing M2M table for field observers on 'PM_Task'
        db.delete_table(db.shorten_name(u'PManager_pm_task_observers'))

        # Removing M2M table for field perhapsResponsible on 'PM_Task'
        db.delete_table(db.shorten_name(u'PManager_pm_task_perhapsResponsible'))

        # Removing M2M table for field viewedUsers on 'PM_Task'
        db.delete_table(db.shorten_name(u'PManager_pm_task_viewedUsers'))

        # Removing M2M table for field files on 'PM_Task'
        db.delete_table(db.shorten_name(u'PManager_pm_task_files'))

        # Removing M2M table for field files_ro on 'PM_Task'
        db.delete_table(db.shorten_name(u'PManager_pm_task_files_ro'))

        # Removing M2M table for field files_eo on 'PM_Task'
        db.delete_table(db.shorten_name(u'PManager_pm_task_files_eo'))

        # Deleting model 'PM_Timer'
        db.delete_table(u'PManager_pm_timer')

        # Deleting model 'PM_Properties'
        db.delete_table(u'PManager_pm_properties')

        # Deleting model 'PM_Property_Values'
        db.delete_table(u'PManager_pm_property_values')

        # Deleting model 'PM_Task_Message'
        db.delete_table(u'PManager_pm_task_message')

        # Removing M2M table for field files on 'PM_Task_Message'
        db.delete_table(db.shorten_name(u'PManager_pm_task_message_files'))

        # Deleting model 'PM_Role'
        db.delete_table(u'PManager_pm_role')

        # Deleting model 'PM_ProjectRoles'
        db.delete_table(u'PManager_pm_projectroles')

        # Deleting model 'PM_User_PlanTime'
        db.delete_table(u'PManager_pm_user_plantime')

        # Deleting model 'PM_Reminder'
        db.delete_table(u'PManager_pm_reminder')

        # Deleting model 'PM_Holidays'
        db.delete_table(u'PManager_pm_holidays')

        # Deleting model 'RatingHistory'
        db.delete_table(u'PManager_ratinghistory')

        # Deleting model 'FineHistory'
        db.delete_table(u'PManager_finehistory')

        # Deleting model 'Credit'
        db.delete_table(u'PManager_credit')

        # Deleting model 'PaymentRequest'
        db.delete_table(u'PManager_paymentrequest')

        # Deleting model 'Fee'
        db.delete_table(u'PManager_fee')

        # Deleting model 'PM_Achievement'
        db.delete_table(u'PManager_pm_achievement')

        # Deleting model 'PM_Project_Achievement'
        db.delete_table(u'PManager_pm_project_achievement')

        # Deleting model 'PM_User_Achievement'
        db.delete_table(u'PManager_pm_user_achievement')

        # Deleting model 'Specialty'
        db.delete_table(u'PManager_specialty')

        # Deleting model 'PM_User'
        db.delete_table(u'PManager_pm_user')

        # Removing M2M table for field trackers on 'PM_User'
        db.delete_table(db.shorten_name(u'PManager_pm_user_trackers'))

        # Removing M2M table for field specialties on 'PM_User'
        db.delete_table(db.shorten_name(u'PManager_pm_user_specialties'))

        # Deleting model 'PMTelegramUser'
        db.delete_table(u'PManager_pmtelegramuser')

        # Deleting model 'PMUserWorkload'
        db.delete_table(u'PManager_pmuserworkload')

        # Deleting model 'PM_Notice'
        db.delete_table(u'PManager_pm_notice')

        # Deleting model 'PM_NoticedUsers'
        db.delete_table(u'PManager_pm_noticedusers')

        # Deleting model 'Agent'
        db.delete_table(u'PManager_agent')

        # Deleting model 'LogData'
        db.delete_table(u'PManager_logdata')

        # Deleting model 'AccessInterface'
        db.delete_table(u'PManager_accessinterface')

        # Removing M2M table for field access_roles on 'AccessInterface'
        db.delete_table(db.shorten_name(u'PManager_accessinterface_access_roles'))

        # Deleting model 'TaskDraft'
        db.delete_table(u'PManager_taskdraft')

        # Removing M2M table for field users on 'TaskDraft'
        db.delete_table(db.shorten_name(u'PManager_taskdraft_users'))

        # Removing M2M table for field tasks on 'TaskDraft'
        db.delete_table(db.shorten_name(u'PManager_taskdraft_tasks'))

        # Removing M2M table for field specialties on 'TaskDraft'
        db.delete_table(db.shorten_name(u'PManager_taskdraft_specialties'))

        # Deleting model 'SimpleMessage'
        db.delete_table(u'PManager_simplemessage')

        # Deleting model 'Conditions'
        db.delete_table(u'PManager_conditions')

        # Deleting model 'Test'
        db.delete_table(u'PManager_test')

        # Deleting model 'Agreement'
        db.delete_table(u'PManager_agreement')

        # Deleting model 'Integration'
        db.delete_table(u'PManager_integration')

        # Deleting model 'SlackIntegration'
        db.delete_table(u'PManager_slackintegration')

        # Deleting model 'PM_MilestoneChanges'
        db.delete_table(u'PManager_pm_milestonechanges')

        # Deleting model 'Feedback'
        db.delete_table(u'PManager_feedback')


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
            'code': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '32'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'credits'", 'null': 'True', 'to': "orm['PManager.PM_Milestone']"}),
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
            'attach': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'authorId': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'files'", 'null': 'True', 'to': "orm['PManager.PM_File_Category']"}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'double': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'delay_deduction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'delay_factor': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'extra_hours': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'fact_close_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'file_for_client': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'final_delay': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'g_factor': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_md5': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'is_close_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_half_completed': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'is_has_grooming': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'milestones'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'overdue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'milestones'", 'to': "orm['PManager.PM_Project']"}),
            'responsible': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': '0', 'max_length': '25', 'null': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'PManager.pm_milestonechanges': {
            'Meta': {'object_name': 'PM_MilestoneChanges'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changes'", 'to': "orm['PManager.PM_Milestone']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'PManager.pm_milestonedevpaymentapproval': {
            'Meta': {'unique_together': "(('milestone', 'user'),)", 'object_name': 'PM_MilestoneDevPaymentApproval'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['PManager.PM_Milestone']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
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
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2021, 5, 24, 0, 0)'}),
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
            'category': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'category'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['PManager.PM_File_Category']", 'blank': 'True', 'unique': 'True'}),
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
            'files_eo': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'fileTasksEO'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['PManager.PM_Files']"}),
            'files_ro': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'fileTasksRO'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['PManager.PM_Files']"}),
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
            'planTimeMainOrg': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'planTimeRegulator': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
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
            'text_eo': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'text_ro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
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
            'avatar_color': ('django.db.models.fields.CharField', [], {'default': "'#cd5555'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
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
            'telegram': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'telegram_id': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
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
        'PManager.pmtelegramuser': {
            'Meta': {'object_name': 'PMTelegramUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'telegram': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'telegram_id': ('django.db.models.fields.CharField', [], {'max_length': '70', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'telegram_user'", 'unique': 'True', 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'PManager.pmuserworkload': {
            'Meta': {'object_name': 'PMUserWorkload'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'workloads'", 'to': "orm['PManager.PMTelegramUser']"}),
            'workload': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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