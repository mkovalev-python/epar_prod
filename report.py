import datetime
from docxtpl import DocxTemplate

def report(tree_tasks):
    doc = DocxTemplate("./tracker/media/template.docx")
    context = {'company_name': "World company"}
    doc.render(context)
    doc.save("./tracker/media/Report_" + datetime.datetime.now().strftime("%d_%m_%Y_%H_%M") + ".docx")
    return "/protected/media/Report_" + datetime.datetime.now().strftime("%d_%m_%Y_%H_%M") + ".docx"