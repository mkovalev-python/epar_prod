# -*- coding:utf-8 -*-
__author__ = 'Rayleigh'

from django.http import HttpResponseForbidden, HttpResponse
from PManager.services.access import assets_access
from PManager.widgets.project_statistic.widget import SumLoanChart
from PManager.viewsExt.tools import templateTools
from PManager.models import PM_Project
import headers

import datetime
import xlsxwriter
import StringIO
from django.utils import timezone


def protected_file(request):
    if not assets_access(request.user, request.GET.get('uri', None)):
        return HttpResponseForbidden()
    response = HttpResponse()
    response['X-Accel-Redirect'] = request.GET.get('uri', None)
    response['Content-Type'] = ''
    return response

def stat_excel(request):
    if 'excel' in request.GET:
        filter = {}
        now = timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone())
        daysBeforeNowForStartFilt = 7
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        headerValues = headers.initGlobals(request)

        if date_from:
            filter['dateFrom'] = templateTools.dateTime.convertToDateTime(date_from)
        else:
            filter['dateFrom'] = now - datetime.timedelta(days=daysBeforeNowForStartFilt)

        if date_to:
            filter['dateTo'] = templateTools.dateTime.convertToDateTime(date_to)
        else:
            filter['dateTo'] = now

        filter['projects'] = []
        if headerValues['CURRENT_PROJECT']:
            filter['projects'].append(headerValues['CURRENT_PROJECT'].id)

        projects = PM_Project.objects.filter(closed=False, locked=False)
        if filter['projects']:
            projects = projects.filter(id__in=filter['projects'])

        loanChart = SumLoanChart(filter['dateFrom'], filter['dateTo'], projects, request.user)

        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output)
        if request.GET.get('excel') == 'loan':
            workbook = loanChart.excel(workbook)

        workbook.close()

        xlsx_data = output.getvalue()

        response = HttpResponse(xlsx_data, mimetype='application/vnd.ms-excel')
        response['Content-Type'] = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment; filename=report.xlsx'

        return response
