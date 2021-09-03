# -*- coding: utf-8 -*-
import datetime
from docxtpl import DocxTemplate

def report(tree_tasks):
    from docxtpl import DocxTemplate
    import jinja2

    jinja_env = jinja2.Environment()


    # to create new filters, first create functions that accept the value to filter
    # as first argument, and filter parameters as next arguments
    def my_filterA(value, my_string_arg):
        return_value = value + ' ' + my_string_arg
        return return_value


    def my_filterB(value, my_float_arg):
        return_value = value + my_float_arg
        return return_value


    # Then, declare them to jinja like this :
    jinja_env.filters['my_filterA'] = my_filterA
    jinja_env.filters['my_filterB'] = my_filterB


    context = {'company_name': 'Hello'}

    tpl = DocxTemplate("./tracker/media/template (1).docx")
    tpl.render(context.decode('utf-8'), jinja_env)

    src = "./tracker/media/Report_" + datetime.datetime.now().strftime(
        "%d_%m_%Y_%H_%M") + ".docx"
    tpl.save(src)
    return "/protected/media/Report_" + datetime.datetime.now().strftime("%d_%m_%Y_%H_%M") + ".docx"
