# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Files, PM_File_Category
from PManager.templatetags.thumbnail import thumbnail, protected
import os


def widget(request, headerValues, ar, qargs):
    if not headerValues['CURRENT_PROJECT']:
        return {
            'redirect': '/'
        }

    files = PM_Files.objects.order_by('name').filter(
        fileTasks__isnull=True,
        msgTasks__isnull=True,
        projectId=headerValues['CURRENT_PROJECT']
    ).exclude(is_old_version=True)
    categories = PM_File_Category.objects.filter(projects=headerValues['CURRENT_PROJECT']).order_by('name')
    categoriesArray = []

    for category in categories:
        categoriesArray.append(category)

    def build_tree(categoriesArray):
        treeAll = build_tree_recursive(None, categoriesArray)

        return treeAll

    def build_tree_recursive(parent, nodes):
        tree = []
        children = []
        for n in nodes:
            if (parent and n.parent and parent == n.parent.id) or (parent == None and not n.parent):
                children.append(n)

        # build a subtree for each child
        for child in children:
            # start new subtree
            obj = {
                'id': child.id,
                'name': child.name
            }
            # call recursively to build a subtree for current node
            obj['children'] = build_tree_recursive(obj['id'], nodes)
            tree.append(obj)

        return tree

    with file(os.path.dirname(os.path.realpath(__file__)) + '/templates/file.html') as f:
        fileTpl = f.read()

    aFiles = []
    for fileObject in files:
        fileJson = fileObject.getJson()

        fileJson.update({
            'src': '/docx/?f=' + str(fileJson['id']) if fileJson['type'] in ['docx', 'xlsx'] else '',
            'resolution': '' if fileObject.isPicture else '',
            'thumbnail': protected(thumbnail(str(fileObject), '200x200')) if fileObject.isPicture else ''
        })
        aFiles.append(fileJson)

    return {
        'files': aFiles,
        'project': headerValues['CURRENT_PROJECT'],
        'tree': build_tree(categoriesArray),
        'fileTemplate': fileTpl
    }
