import datetime
from docxtpl import DocxTemplate

def report(tree_tasks):
    from docxtpl import DocxTemplate
    import jinja2

    jinja_env = jinja2.Environment()

    context = {'company_name': 'Hello'}
    print(context)
    tpl = DocxTemplate("./tracker/media/template (1).docx")
    print(tpl.docx.element.xml)
    tpl.render(context, jinja_env)

    src = "./tracker/media/Report_" + datetime.datetime.now().strftime(
        "%d_%m_%Y_%H_%M") + ".docx"
    tpl.save(src)
    return "/protected/media/Report_" + datetime.datetime.now().strftime("%d_%m_%Y_%H_%M") + ".docx"
