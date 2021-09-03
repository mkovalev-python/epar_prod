import datetime
from docxtpl import DocxTemplate

def report(tree_tasks):
    from django.core.files.base import ContentFile, File
    from django.core.files.storage import default_storage
    list_task = []
    for _ in task_list:
        list_task.append(
            {'name': _.name, 'text': _.text, 'text_eo': _.text_eo, 'prefix':_.prefix,
             'text_ro': _.text_ro})
    response = requests.get(
        "http://94.26.245.131:4000/report/",
        data={'data': json.dumps(list_task)},
        verify=False)
    if response.status_code == 200:
        path = default_storage.save('Report1.docx', ContentFile(response.content))
        return "/protected/media/"+path.encode('utf-8')
    else:
        return "/"
