# -*- coding:utf-8 -*-
__author__ = 'Gvammer'

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Max
from django.utils.timezone import now

from PManager.models import Credit, Specialty, \
    LogData, Agent, PM_File_Category, PM_Milestone, \
    PM_NoticedUsers, PM_Notice, PM_Task_Status, \
    PM_User_PlanTime, PM_Files, PM_Task_Message, \
    PM_Timer, PM_Role, PM_Task, PM_ProjectRoles, \
    PM_Properties, PM_Project, PM_Tracker, PM_User, Agreement, \
    PM_User_Achievement, PM_Achievement, AccessInterface, \
    PM_Reminder, PM_Project_Achievement, Conditions, Test, Fee, TaskDraft, PaymentRequest, \
    RatingHistory, FineHistory, Release, SlackIntegration, PM_MilestoneChanges, Feedback, \
    PM_MilestoneStatus, PM_Holidays, PMUserWorkload, PMTelegramUser, PM_MilestoneDevPaymentApproval


class UserRolesInline(admin.TabularInline):
    fieldsets = (
        (
            None,
            {
                'fields': ('user', 'project', 'role',)
            }
        ),
    )

    model = PM_ProjectRoles
    extra = 0


class FeedbackInline(admin.ModelAdmin):
    list_display = ['user', 'project', 'meeting_time', 'demo_value', 'standup',
                    'speed', 'quality', 'notes_communications', 'notes_quality',
                    'rating', 'notes_was', 'notes_do']
    list_filter = ['user', 'project']


class CreditInline(admin.ModelAdmin):
    list_display = ['user', 'payer', 'get_project', 'value', 'type', 'date', 'task']
    list_filter = ['user', 'payer', 'milestone']

    def get_project(self, obj):
        return obj.milestone.project

    get_project.short_description = u'Проект'
    get_project.admin_order_field = 'milestone__project'


class TaskInline(admin.ModelAdmin):
    list_display = ('name', 'project', 'milestone', 'author',  'resp')
    list_filter = ['resp', 'project']


class RatingInline(admin.ModelAdmin):
    list_display = ['user', 'value', 'dateCreate']
    list_filter = ['user']


class FeeInline(admin.ModelAdmin):
    list_display = ['user', 'project', 'value', 'date', 'task']
    list_filter = ['user', 'project__name']


class UserRoles(admin.ModelAdmin):
    list_display = ['user', 'project', 'role']
    list_filter = ['user', 'project', 'role__code']


class LogDatas(admin.ModelAdmin):
    list_display = ['code', 'value', 'datetime', 'project_id', 'user']


class Timers(admin.ModelAdmin):
    list_display = ['seconds', 'user', 'dateEnd', 'task']


class PaymentsInline(admin.ModelAdmin):
    list_display = ['user', 'payer', 'project', 'value', 'date']


class Reminder(admin.ModelAdmin):
    list_display = ['user', 'task', 'date']


class AgreementInline(admin.ModelAdmin):
    list_display = ['date', 'resp', 'payer']


class PM_MilestoneChangesInline(admin.ModelAdmin):
    list_display = ['date', 'value', 'milestone']


class PM_UserAdmin(admin.ModelAdmin):
    list_display = ['user', 'sp_price', 'hoursQtyPerDay']


def close_milestones(modeladmin, request, queryset):
    for item in queryset:
        item.close_milestone(now(), request.user)
close_milestones.short_description = u"Закрыть спринты"


class PM_MilestoneStatusInline(admin.TabularInline):
    model = PM_MilestoneStatus
    extra = 1
    fields = ('status', 'start_date', 'end_date', 'comment', 'author', 'date_create')
    readonly_fields = ('date_create',)
    classes = ['collapse']


class PM_MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'closed', 'date', '_delays_day', 'delay_deduction', 'final_delay', '_support_url')
    list_filter = ('closed', 'project')
    readonly_fields = ('_delays_day', '_support_url', )
    actions = (close_milestones, )
    inlines = (PM_MilestoneStatusInline,)
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': ('name', '_support_url', 'text', 'target', 'criteria', 'file_for_client', 'date', 'critically',
                       'extra_hours', 'project', 'overdue', '_delays_day', 'delay_deduction', 'final_delay',
                       'responsible', 'closed', 'is_close_confirmed', 'manager', 'type', 'fact_close_date', )
        }),
        (u'Коэффициенты', {'fields': ('is_half_completed', 'is_has_grooming', 'delay_factor', 'g_factor')}),
    )

    def queryset(self, request):
        qs = super(PM_MilestoneAdmin, self).queryset(request)
        self.request = request
        return qs

    def _support_url(self, obj):
        return 'https://' + self.request.META['HTTP_HOST'] + obj.support_url

    _support_url.short_description = u'URL для поддержки'

    def _delays_day(self, obj):
        return obj.delay_days

    _delays_day.short_description = u'Просрочка'


class PM_ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', '_support_url')
    save_on_top = True

    def queryset(self, request):
        qs = super(PM_ProjectAdmin, self).queryset(request)
        self.request = request
        return qs

    def _support_url(self, obj):
        return 'https://' + self.request.META['HTTP_HOST'] + obj.support_url

    _support_url.short_description = u'URL для поддержки'


class WorkloadLatestFilter(SimpleListFilter):
    title = u'Последние ответы'
    parameter_name = 'latest_workload'

    def lookups(self, request, model_admin):
        return (
            ('latest', u'Последние'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'latest':
            latest = PMUserWorkload.objects.values('user').annotate(latest_id=Max('id'))
            latest_ids = [item['latest_id'] for item in latest]
            return queryset.filter(id__in=latest_ids)


class PMUserWorkloadAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'workload', 'date')
    list_filter = (WorkloadLatestFilter, )

    def user_name(self, obj):
        try:
            return obj.user.user.get_full_name()
        except AttributeError:
            return obj.user

    user_name.short_description = u'Пользователь'


class PMTelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram', 'telegram_id')


class PM_MilestoneDevPaymentApprovalAdmin(admin.ModelAdmin):
    list_display = ('milestone', 'user', 'is_approved', 'created', 'modified')


admin.site.register(PM_Role)
admin.site.register(PM_Task, TaskInline)
admin.site.register(PM_ProjectRoles, UserRoles)
admin.site.register(PM_Properties)
admin.site.register(PM_Project, PM_ProjectAdmin)
admin.site.register(PM_Tracker)
admin.site.register(PM_User, PM_UserAdmin)
admin.site.register(PM_Files)
admin.site.register(PM_Task_Message)
admin.site.register(PM_Timer, Timers)
admin.site.register(PM_Achievement)
admin.site.register(PM_User_Achievement)
admin.site.register(PM_Project_Achievement)
admin.site.register(PM_User_PlanTime)
admin.site.register(PM_Task_Status)
admin.site.register(PM_Notice)
admin.site.register(PM_NoticedUsers)
admin.site.register(PM_Milestone, PM_MilestoneAdmin)
admin.site.register(PM_File_Category)
admin.site.register(PM_Reminder, Reminder)
admin.site.register(Agent)
admin.site.register(LogData, LogDatas)
admin.site.register(Specialty)
admin.site.register(Credit, CreditInline)
admin.site.register(Fee, FeeInline)
admin.site.register(AccessInterface)
admin.site.register(Test)
admin.site.register(Conditions)
admin.site.register(TaskDraft)
admin.site.register(PaymentRequest)
admin.site.register(RatingHistory, RatingInline)
admin.site.register(FineHistory)
admin.site.register(Agreement, AgreementInline)
admin.site.register(SlackIntegration)
admin.site.register(Release)
admin.site.register(Feedback, FeedbackInline)
admin.site.register(PM_MilestoneChanges, PM_MilestoneChangesInline)
admin.site.register(PM_Holidays)
admin.site.register(PMUserWorkload, PMUserWorkloadAdmin)
admin.site.register(PMTelegramUser, PMTelegramUserAdmin)
admin.site.register(PM_MilestoneDevPaymentApproval, PM_MilestoneDevPaymentApprovalAdmin)


from django.contrib.auth.admin import UserAdmin

UserAdmin.list_display += ('id',)
