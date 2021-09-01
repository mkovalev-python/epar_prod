# -*- coding: utf-8 -*-
import datetime
from docxtpl import DocxTemplate

def report(tree_tasks):
    from docxtpl import DocxTemplate
    from cgi import escape
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    doc = DocxTemplate("./tracker/media/template.docx")
    context = {'company_name': "World company"}
    context = {'company_name': escape("World company")}
    doc.render(context.encode('utf-8'))

    src = "./tracker/media/Report_" + datetime.datetime.now().strftime(
        "%d_%m_%Y_%H_%M") + ".docx"
    doc.save(src)
    return "/protected/media/Report_" + datetime.datetime.now().strftime("%d_%m_%Y_%H_%M") + ".docx"
