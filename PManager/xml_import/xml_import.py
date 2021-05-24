# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from django.shortcuts import HttpResponse
from django.template import loader,  RequestContext
from django.contrib.auth.models import User
import zipfile
import os.path
from tracker import settings
from xml.dom.minidom import parse, parseString
from django.core.files.base import ContentFile
from xml.dom import pulldom

from PManager.models.tasks import PM_Files, PM_Task, PM_Task_Message, PM_Project

def find_files(catalog, f):
    find_dirs = []
    find_files = []

    for root, dirs, files in os.walk(catalog):
        find_dirs += [os.path.join(root, name) for name in dirs if name == f]

    for dir in find_dirs:
        for root, dirs, files in os.walk(dir):
            find_files += [os.path.join(root, name) for name in files]

    return find_files

class XML_Import:
    @staticmethod
    def importView(request):
        aProjectMatch = {
            '175349':'1',
            '184101':'11',
            '271950':'18',
            '271959':'19',
            '271960':'20',
            '271969':'16',
            '316681':'21',
            '317298':'15',
            '422647':'22'
        }
        aTasks = []
        aUsersMatch = {
            'dc383a63-d8f7-4949-9a15-e287a4d7643d':'1',
            '2d64667f-7d48-4f8e-92ef-36d791e38165':'27',#emaslenkov,
            '69ec43bd-942e-45c2-8006-7bd7a1643793':'6',#aermashov,
            'f42b0898-41a3-45c3-a365-29d5608ebc06':'1',#egor test,
            'e7a5ba20-a86e-47b3-84bc-fc55117b3419':'22',#savitskiy,
            '3d47b187-4fb7-4539-acdb-b8261dcdcd45':'28',#nikkirs,
            '63549d00-330b-4456-9ccf-bcd6527a832e':'29',#pv.vibornov,
            'de9ec3cd-106c-44c5-a37c-d12809190be1':'2',#ugeeeen,
            'b465b3ff-359c-4c8c-b2ac-1339373197e2':'5',#arnautov,
            '842d80d3-fabb-426c-a1b5-39ca9bce43c8':'29',#pv.vibornov,
            'f1566006-bcd6-4e3f-8f9d-5e8313eaed08': '30',#asmirnov
            'd785d7df-6a60-4a4c-88a4-342b897eee37': '31',#akhananov
            '4c0f0937-95b3-449c-81bd-0e84f05466df': '32', #pgeleyshev
            '0eae6672-88fd-4c28-bce1-a44fdee3cd43': '33', #atrofimov
            'eb6e7336-a561-4d50-8635-3e9ab102d715': '23', #achernenko
            'e95c87e1-30fc-4031-ae1c-e2bf63f8e036': '6', #aermashov
            '42dd9934-3684-4465-84c1-43f5a26810eb': '1', #emaslov
            '498b1589-d29a-44d1-a577-019fa728e7b4': '22', #isavitkyi
            '4213b44d-1554-4307-8b98-c2d39dcf1ccb': '34', #nagumanov
            '55a19c0d-4386-425b-9a2f-c38a5b8ebd17': '24', #agalendr
            '0047036a-639c-4000-8f0a-fc64eb93a26d': '18', #vbelykh
            '36f00cae-816b-427b-848d-aee8e8a17187': '5' #varnautov
        }
        #todo: add code for create projects and users
        sUploadPath = os.path.join(settings.PROJECT_ROOT, "PManager/static/upload")
        sImportPath = os.path.join(sUploadPath, 'import')
        if request.POST.get('import_start', None):
            sFilePath = request.POST.get('path_to_file', None)
            sDirPath = request.POST.get('path_to_dir', None)
            if not os.path.exists(sImportPath):
                os.mkdir(sImportPath)
            if sFilePath:
                sFilePath = os.path.join(sUploadPath,sFilePath)
                zFile = zipfile.ZipFile(sFilePath)
                for name in zFile.namelist():
                    (dirname, filename) = os.path.split(name)

                    dirname = os.path.join(sImportPath,dirname)
                    try:
                        newName = name.decode('UTF-8').encode('UTF-8')
                    except:
                        try:
                            newName = name.decode('cp866').encode('UTF-8')
                        except:
                            newName = name.decode('cp1251').encode('UTF-8')

                    #newName = newName.replace(' ','').replace('/','\\')

                    newName = os.path.join(sImportPath,newName)

                    if not os.path.exists(dirname):
                        os.mkdir(dirname)
                    if filename:
                        try:
                            fd = open(newName,"w")
                            fd.write(zFile.read(name))
                            fd.close()
                        except:
                            pass
#                print zFile
            elif sDirPath:
                sDirPath = os.path.join(sImportPath,sDirPath)
                sProjectsPath = os.path.join(sDirPath,'databases/core/projects_tasks')
                sCommentsPath = os.path.join(sDirPath,'databases/core/projects_comments')
                sFilesPath = os.path.join(sDirPath,'databases/core/files_file')
                sFilesTagPath = os.path.join(sDirPath,'databases/core/files_tag')
                sFilesTagLinkPath = os.path.join(sDirPath,'databases/core/files_tag_link')
                sSubtasksPath = os.path.join(sDirPath,'databases/core/projects_subtasks')
                sFilesDirPath = os.path.join(sDirPath,'files')
                domTasks = parse(sProjectsPath)
                domSubtasks = parse(sSubtasksPath)
                domComments = parse(sCommentsPath)
                domFiles = parse(sFilesPath)
                domFilesTag = parse(sFilesTagPath)
                domFilesTagLink = parse(sFilesTagLinkPath)


                commentsTask = domComments.getElementsByTagName('projects_comments')
                aSubTasks = domSubtasks.getElementsByTagName('projects_subtasks')
                aTagLinks = domFilesTagLink.getElementsByTagName('files_tag_link')
                fileTag = domFilesTag.getElementsByTagName('files_tag')
                files = domFiles.getElementsByTagName('files_file')
                arTags = {}
                for tagNode in fileTag:
                    task_id = tagNode.getElementsByTagName('name')[0].firstChild.nodeValue[4:]
                    tag_id = tagNode.getElementsByTagName('id')[0].firstChild.nodeValue
                    arTags[tag_id] = task_id

                aTaskFiles = {}

                for taglink in aTagLinks:
                    file_id = taglink.getElementsByTagName('entry_id')[0].firstChild.nodeValue
                    tag_id = taglink.getElementsByTagName('tag_id')[0].firstChild.nodeValue
                    task_id = arTags.get(tag_id, 0)
                    if not aTaskFiles.get(task_id, None):
                        aTaskFiles[task_id] = []
                    aTaskFiles[task_id].append(file_id)

#                del arTags
                del domFilesTag
                del domFilesTagLink
                del fileTag
                del aTagLinks
                aComments = {}
                #соберем только комменты, относящиеся к таскам
                for comment in commentsTask:
                    if 'Task' == comment.getElementsByTagName('target_uniq_id')[0].firstChild.nodeValue[:4]:
                        aComment = {}
                        for attr in comment.childNodes:
                            if hasattr(attr, 'tagName'):
                                aComment[attr.tagName] =  comment.getElementsByTagName(attr.tagName)[0].firstChild.nodeValue if comment.getElementsByTagName(attr.tagName)[0].firstChild else None
                        taskId = aComment['target_uniq_id'][5:]

                        if not aComments.get(taskId, None): aComments[taskId] = []
                        aComments[taskId].append(aComment)
                del commentsTask

                for el in domTasks.getElementsByTagName('projects_tasks'):
                    taskObj = {}

                    for attr in el.childNodes:
                        if hasattr(attr, 'tagName'):
                            taskObj[attr.tagName] =  el.getElementsByTagName(attr.tagName)[0].firstChild.nodeValue if el.getElementsByTagName(attr.tagName)[0].firstChild else None

                    if taskObj['project_id'] in aProjectMatch.keys():
                        taskObj['subtasks'] = []

                        projectId = aProjectMatch[taskObj['project_id']]
                        userId = aUsersMatch[taskObj['create_by']] if taskObj['create_by'] in aUsersMatch else None
                        try:
                            task = PM_Task.objects.get(name=taskObj['title'], project=PM_Project.objects.get(pk=projectId))
                            if task.closed and taskObj['status'] == u'1':
                                task.closed = False
                                task.save()

                            for domSubtask in aSubTasks:
                                iTaskId = domSubtask.getElementsByTagName('task_id')[0].firstChild.nodeValue
                                if iTaskId == taskObj['id']:
                                    oSubtaskData = {}
                                    for attr in domSubtask.childNodes:
                                        if hasattr(attr, 'tagName'):
                                            oSubtaskData[attr.tagName] =  domSubtask.getElementsByTagName(attr.tagName)[0].firstChild.nodeValue if domSubtask.getElementsByTagName(attr.tagName)[0].firstChild else None
                                    try:
                                        try:
                                            subtask = PM_Task.objects.get(name=oSubtaskData['Title'], parentTask=task.id, project=PM_Project.objects.get(pk=projectId))
                                            if not subtask.closed and taskObj['status'] == u'2':
                                                subtask.closed = True
                                                subtask.save()

                                        except PM_Task.DoesNotExist:
                                            subtask = PM_Task(name=oSubtaskData['Title'], text=oSubtaskData['Title'])

                                            iSubtaskCreatedBy = aUsersMatch[oSubtaskData['create_by']] if oSubtaskData['create_by'] in aUsersMatch else None
                                            iSubtaskResponsible = aUsersMatch[oSubtaskData['responsible_id']] if oSubtaskData['responsible_id'] in aUsersMatch else None

                                            subtask.project = task.project
                                            subtask.parentTask = task
                                            subtask.author = User.objects.get(pk=iSubtaskCreatedBy)
                                            subtask.dateCreate = oSubtaskData['create_on'].replace('T',' ')
                                            subtask.closed = True
                                            subtask.project_knowledge = 0.11
                                            subtask.save()
                                            if iSubtaskResponsible and iSubtaskResponsible in aUsersMatch.keys():
                                                try:
                                                    k=0
                                                    subtask.responsible.add(User.objects.get(pk=iSubtaskResponsible))
                                                except User.DoesNotExist:
                                                    pass
                                    except Exception:
                                        pass

                            taskObj['comments'] = aComments.get(taskObj['id'],[])
                            for comment in taskObj['comments']:
                                if comment['content'].find('https://s3.amazonaws.com/data.teamlab.com/07/35/68/fckuploaders'):
                                    comment['content'] = comment['content'].replace('https://s3.amazonaws.com/data.teamlab.com/07/35/68/fckuploaders', '/static')

                                try:
                                    try:
                                        comment = PM_Task_Message.objects.get(text=comment['content'], task=task)
                                    except PM_Task_Message.DoesNotExist:
                                        message = PM_Task_Message(text=comment['content'])
                                        message.dateCreate = comment['create_on'].replace('T',' ')
                                        message.task = task
                                        if comment['create_by']:
                                            try:
                                                message.author = User.objects.get(pk=aUsersMatch[comment['create_by']])
                                            except User.DoesNotExist:
                                                pass

                                        try:
                                            message.save()
                                        except:
                                            pass
                                except Exception:
                                    pass

                        except PM_Task.DoesNotExist:
                            task = PM_Task(
                                name=taskObj['title'],
                                text=taskObj['description'] if taskObj.get('description',None) else ''
                            )
                            task.project = PM_Project.objects.get(pk=projectId)
                            task.author = User.objects.get(pk=userId) if userId else request.user
                            if userId:
                                roles = task.author.get_profile().getRoles(task.project)
                                if not roles:
                                    task.author.get_profile().setRole('employee', task.project)

                            task.deadline = taskObj['deadline'].replace('T',' ') if taskObj['deadline'] != '0001-01-01T00:00:00' else None
                            task.dateCreate = taskObj['create_on'].replace('T',' ')
                            task.closed = True
                            task.project_knowledge = 0.11

                            try:
                                task.save()
                            except:
                                continue

                            for domSubtask in aSubTasks:
                                iTaskId = domSubtask.getElementsByTagName('task_id')[0].firstChild.nodeValue
                                if iTaskId == taskObj['id']:
                                    oSubtaskData = {}
                                    for attr in domSubtask.childNodes:
                                        if hasattr(attr, 'tagName'):
                                            oSubtaskData[attr.tagName] =  domSubtask.getElementsByTagName(attr.tagName)[0].firstChild.nodeValue if domSubtask.getElementsByTagName(attr.tagName)[0].firstChild else None
                                    iSubtaskCreatedBy = aUsersMatch[oSubtaskData['create_by']] if oSubtaskData['create_by'] in aUsersMatch else None
                                    iSubtaskResponsible = aUsersMatch[oSubtaskData['responsible_id']] if oSubtaskData['responsible_id'] in aUsersMatch else None

                                    subtask = PM_Task(name=oSubtaskData['Title'], text=oSubtaskData['Title'])
                                    subtask.project = task.project
                                    subtask.parentTask = task
                                    subtask.author = User.objects.get(pk=iSubtaskCreatedBy)
                                    subtask.dateCreate = oSubtaskData['create_on'].replace('T',' ')
                                    subtask.closed = True
                                    subtask.project_knowledge = 0.11
                                    subtask.save()
                                    if iSubtaskResponsible and iSubtaskResponsible in aUsersMatch.keys():
                                        try:
                                            k=0
                                            subtask.responsible.add(User.objects.get(pk=iSubtaskResponsible))
                                        except User.DoesNotExist:
                                            pass
                                    taskObj['subtasks'].append(oSubtaskData)

                            if taskObj['responsible_id'] and taskObj['responsible_id'] in aUsersMatch.keys():
                                try:
                                    oResponsible = User.objects.get(pk=aUsersMatch[taskObj['responsible_id']])
                                    task.responsible.add(oResponsible)
                                    roles = oResponsible.get_profile().getRoles(task.project)
                                    if not roles:
                                        oResponsible.get_profile().setRole('employee', task.project)
                                except User.DoesNotExist:
                                    pass

                            taskObj['comments'] = aComments.get(taskObj['id'],[])
                            taskObj['files'] = aTaskFiles.get(taskObj['id'],[])
                            taskObj['filesReal'] = []
                            for file in taskObj['files']:
                                taskObj['filesReal'] += find_files(sFilesDirPath,'file_'+file)


                            for realFile in taskObj['filesReal']:
                                file = PM_Files(project=task.project, authorId=task.author)

                                file.file.save(realFile.split('/')[-1], ContentFile(open(realFile,'rb').read()))
                                file.save()
                                task.files.add(file)

                            for comment in taskObj['comments']:
                                if comment['content'].find('https://s3.amazonaws.com/data.teamlab.com/07/35/68/fckuploaders'):
                                    comment['content'] = comment['content'].replace('https://s3.amazonaws.com/data.teamlab.com/07/35/68/fckuploaders', '/static')
                                message = PM_Task_Message(text=comment['content'])
                                message.dateCreate = comment['create_on'].replace('T',' ')
                                message.task = task
                                if comment['create_by']:
                                    try:
                                        message.author = User.objects.get(pk=aUsersMatch[comment['create_by']])
                                    except User.DoesNotExist:
                                        pass
                                try:
                                    message.save()
                                except:
                                    pass

                            aTasks.append(taskObj)

        c = RequestContext(request,{})
        c.update({'tasks': aTasks})
        t = loader.get_template('xml_import/import_teamlab.html')
        return HttpResponse(t.render(c))