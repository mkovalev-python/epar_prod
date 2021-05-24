# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from tracker.settings import PROJECT_ROOT, HTTP_ROOT_URL, MEDIA_URL, MEDIA_ROOT
from django.shortcuts import HttpResponse
from PManager.models import PM_Files
from django.template import loader, Context
import datetime
import os

def docxView(request):
    #TODO: все к херам переписать по уму
    from shutil import copyfile
    from docx2html import convert

    def handle_image(image_id, relationship_dict):
        image_path = relationship_dict[image_id]
        # Now do something to the image. Let's move it somewhere.
        _, filename = os.path.split(image_path)
        destination_path = os.path.join(MEDIA_ROOT, filename)
        copyfile(image_path, destination_path)

        # Return the `src` attribute to be used in the img tag
        return '/protected%s%s' % (MEDIA_URL, filename)

    fp = request.GET.get('f', None)
    html = None
    if fp:
        try:
            pm_file = PM_Files.objects.get(pk=int(fp))
            if pm_file.type == 'docx':
                html = convert(str(pm_file.file.path), image_handler=handle_image)
            elif pm_file.type == 'xlsx':
                html = excelToHtml(str(pm_file.file.path))
        except PM_Files.DoesNotExist:
            pass
    return HttpResponse(html)

def excelToHtml(path):
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    sheets = wb.get_sheet_names()

    excel = {
        'excel': []
    }

    for sheet in sheets:
        ws = wb.get_sheet_by_name(sheet)
        n = {'name': sheet, 'rows': []}

        for row in ws.rows:
            x = []
            for cell in row:
                x.append(cellType(cell.value))
            n['rows'].append(x)

        excel['excel'].append(n)

    c = Context(excel)
    t = loader.get_template('helpers/excel_view.html')

    return t.render(c)

def cellType(value):
    if isinstance(value, unicode):
        value = u''.join(value).encode('utf-8')

    if isinstance(value, datetime.datetime):
        value = value.strftime('%d.%m.%Y %H:%M')

    if isinstance(value, datetime.time) or isinstance(value, int) or isinstance(value, float):
        value = str(value)

    if value is None:
        value = ''

    return value
