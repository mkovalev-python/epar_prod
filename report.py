# -*- coding: utf-8 -*-
import datetime
from docxtpl import DocxTemplate

def report(tree_tasks):
    from docxtpl import DocxTemplate
    from cgi import escape
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    doc = DocxTemplate("./tracker/media/template (1).docx")
    context = {u'company_name': u"World company"}
    print(context)
    doc.render(context)

    src = "./tracker/media/Report_" + datetime.datetime.now().strftime(
        "%d_%m_%Y_%H_%M") + ".docx"
    doc.save(src)
    return "/protected/media/Report_" + datetime.datetime.now().strftime("%d_%m_%Y_%H_%M") + ".docx"
