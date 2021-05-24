# -*- coding:utf-8 -*-
__author__ = 'Gvammer'

from django.shortcuts import HttpResponse
from PManager.models import PM_Task, PM_Files, PM_File_Category
import base64, os.path, json
from django.core.files.base import ContentFile
from PIL import Image
from PManager.viewsExt import headers
from PManager.viewsExt.tools import taskExtensions
from PManager.templatetags.thumbnail import thumbnail, protected
import hashlib
import time
from django.http import HttpResponseBadRequest, Http404, HttpResponseNotAllowed
from ajaxuploader.backends.local import LocalUploadBackend
from django.core.serializers.json import DjangoJSONEncoder
from tracker import settings


def unicodeToInt(un):
    return int(round(float(un), 0))


def fileSave(request):
    # сохранение файла и ресайз
    # файл изображения вставляется из буфера и передается
    # как текст в base64 закодированном виде
    headerValues = headers.initGlobals(request)
    path = os.path.dirname(os.path.abspath(__file__))
    fileContent = request.POST.get('posted_image', '')
    # получаем из POST координаты квадрата, который будем вырезать из картинки
    x1, y1, x2, y2 = unicodeToInt(request.POST.get('posted_image_x1', 0)), \
                     unicodeToInt(request.POST.get('posted_image_y1', 0)), \
                     unicodeToInt(request.POST.get('posted_image_x2', 0)), \
                     unicodeToInt(request.POST.get('posted_image_y2', 0))

    size_w, size_h = unicodeToInt(request.POST.get('posted_image_size_w', 0)), unicodeToInt(
        request.POST.get('posted_image_size_h', 0))
    if fileContent.find('image/png'):
        # уберем артефакт из закодированного файла
        fileContent = fileContent.split('base64,')[1]

        # сохраним файл в базу
        file = PM_Files(projectId=headerValues['CURRENT_PROJECT'], authorId=request.user)
        file.file.save(
            'projects/' + str(int(headerValues['CURRENT_PROJECT'].id)) + '/pasted.png',
            ContentFile(base64.b64decode(fileContent))
        )

        # откроем картинку для изменений в PIL
        im = Image.open(file.file.path)

        width, height = im.size
        if size_h and size_w and x1:
            k_w, k_h = float(width) / float(size_w), float(height) / float(size_h)

            im = im.crop((int(x1 * k_w), int(y1 * k_h), int(x2 * k_w), int(y2 * k_h)))
            # todo: убрать все, что отвечало за обрезку изображения
            outfile = "tracker/media/tmp/cropped.png"
            im.save(outfile, "PNG")
            file.file.delete()
            # сохраняем картинку в базу
            file.file.save(
                'projects/' + str(int(headerValues['CURRENT_PROJECT'].id)) + '/cropped.png',
                ContentFile(open(outfile, 'rb').read())
            )

        file.save()
        return HttpResponse(json.dumps({'path': str(file.file), 'fid': file.id, 'type': file.type,
                                        'thumbnail': protected(
                                            thumbnail(str(file), '200x200')) if file.isPicture else ''}))
    return HttpResponse(json.dumps({'error': 'PNG expected'}))


def ajaxFilesResponder(request):
    # ajax-респондер для обработки сигналов
    # от виджета file_list
    import re

    def deleteFile(oFile):
        path = oFile.file.path.encode('utf-8')
        if os.path.isfile(path):
            os.remove(path)
        return oFile.delete()

    headerValues = headers.initGlobals(request)
    sectName = re.sub(' +', ' ', request.POST.get('name', '').strip())
    sectId = request.POST.get('section_id', 0)
    parent = int(request.POST.get('parent', 0))
    action = request.POST.get('action', '')
    search = request.POST.get('search', '')
    if sectId == 'tasks':
        files_from_tasks = True
        sectId = 0
    else:
        files_from_tasks = False
        sectId = int(sectId)

    if request.user.is_authenticated():
        # добавление категории
        if action == 'addCategory' and sectName:
            category = PM_File_Category(name=sectName)
            if parent:
                try:
                    category.parent = PM_File_Category.objects.get(id=parent)
                except PM_File_Category.DoesNotExist:
                    pass

            category.save()
            category.projects.add(headerValues['CURRENT_PROJECT'])

            if category.id:
                return HttpResponse(json.dumps({'success': 'Y', 'id': category.id}))

        elif action == 'renameCategory' and sectName and sectId:
            result = {}
            try:
                category = PM_File_Category.objects.get(id=sectId, projects=headerValues['CURRENT_PROJECT'])
                category.name = sectName
                category.save()

                result['success'] = 'Y'
            except PM_File_Category.DoesNotExist():
                result['success'] = 'N'

            return HttpResponse(json.dumps(result))
        # получение списка файлов категории
        elif action == 'getFileList':
            category = None
            if sectId:
                try:
                    category = PM_File_Category.objects.get(pk=sectId, projects=headerValues['CURRENT_PROJECT'])
                except PM_File_Category.DoesNotExist:
                    pass

            files = PM_Files.objects.filter(projectId=headerValues['CURRENT_PROJECT']).exclude(is_old_version=True)
            if category:
                files = files.filter(category=category)
            else:
                files = files.filter(category__isnull=True)

            if not files_from_tasks and not category:
                files = files.filter(fileTasks__isnull=True, msgTasks__isnull=True)

            if search:
                files = files.filter(name__contains=search)

            files = files.order_by('name')

            arFiles = []
            for fileObject in files:
                fileJson = fileObject.getJson()
                fileJson.update({
                    'thumbnail': protected(thumbnail(str(fileObject), '200x200')) if fileObject.isPicture else '',
                    'resolution': '' if fileObject.isPicture else ''
                })
                arFiles.append(fileJson)
            return HttpResponse(json.dumps(arFiles))

        # удаление файлов по массиву ID
        elif action == 'deleteFiles':
            fId = request.POST.getlist('files[]', None)
            if fId:
                print fId
                try:
                    aDeletedFiles = []
                    files = PM_Files.objects.filter(projectId=headerValues['CURRENT_PROJECT'], pk__in=fId)
                    if request.user.get_profile().isManager(headerValues['CURRENT_PROJECT']):
                        for oFile in files:
                            aDeletedFiles.append(oFile.id)
                            deleteFile(oFile)
                        return HttpResponse(json.dumps(aDeletedFiles))

                except PM_Files.DoesNotExist:
                    pass

        # удаление дитректории по ID
        elif action == 'deleteDir':
            iDirId = request.POST.get('dirId', None)

            if iDirId:
                try:
                    dir = PM_File_Category.objects.get(projects=headerValues['CURRENT_PROJECT'], pk=iDirId)
                    if request.user.get_profile().isManager(headerValues['CURRENT_PROJECT']):
                        files = dir.files.all()
                        for file in files:
                            if not file.fileTasks.all():
                                deleteFile(file)
                        dir.delete()
                        return HttpResponse(json.dumps({'success': 'Y'}))

                except PM_File_Category.DoesNotExist:
                    pass

        # перенос файлов в директорию
        elif action == 'replaceFiles':
            iDirId = request.POST.get('section_id', None)
            aFilesId = request.POST.getlist('files[]', None)
            aReplacedFiles = []
            dir = None
            if iDirId:
                try:
                    dir = PM_File_Category.objects.get(projects=headerValues['CURRENT_PROJECT'], pk=iDirId)
                except PM_File_Category.DoesNotExist:
                    pass

            files = PM_Files.objects.filter(projectId=headerValues['CURRENT_PROJECT'], pk__in=aFilesId)
            if request.user.get_profile().isManager(headerValues['CURRENT_PROJECT']):
                for oFile in files:
                    oFile.category = dir
                    oFile.save()
                    aReplacedFiles.append(oFile.id)

                return HttpResponse(json.dumps(aReplacedFiles))

        elif action == 'getVersionsList':
            fileId = request.POST.get('file_id', None)
            if request.user.get_profile().isManager(headerValues['CURRENT_PROJECT']):
                try:
                    file = PM_Files.objects.get(pk=fileId, projectId=headerValues['CURRENT_PROJECT'])
                    versions = file.versions.all()
                    aFiles = taskExtensions.getFileList(versions)

                    return HttpResponse(json.dumps(aFiles))
                except PM_Files.DoesNotExist:
                    pass

    return HttpResponse(json.dumps({'success': 'N'}))


def DeleteUploadedFile(request, handler_id):
    if 'file_id' in request.GET:
        try:
            file = PM_Files.objects.get(pk=int(request.GET['file_id']))
            tasks_count = PM_Task.objects.filter(files=file, active=True).count()
            if tasks_count <= 0:
                file.delete()
                return HttpResponse(
                    json.dumps({"success": True, "file_id": int(request.GET['file_id'])}, cls=DjangoJSONEncoder),
                    content_type='text/html; charset=utf-8')
        except PM_Files.DoesNotExist:
            pass
    return HttpResponse(json.dumps({"success": False}, cls=DjangoJSONEncoder), content_type='text/html; charset=utf-8')


def AjaxAddFile(request):
    if PM_Files.objects.filter(name=request.raw_post_data, double=True, attach=False).exists():
        get_file = PM_Files.objects.get(name=request.raw_post_data, double=True, attach=False)
        i = 1
        while PM_Files.objects.filter(name="(" + str(i) + ")" + request.raw_post_data).exists():
            i += 1
        get_file.name = "(" + str(i) + ')' + request.raw_post_data
        get_file.double = False
        get_file.save()

    return HttpResponse(json.dumps({"success": False}, cls=DjangoJSONEncoder), content_type='text/html; charset=utf-8')


def AjaxAddFastenFile(request):
    get_file = PM_Files.objects.get(name=request.raw_post_data, double=True)
    get_file.double = False
    get_file.attach = True
    get_file.save()
    return HttpResponse(json.dumps({"success": False}, cls=DjangoJSONEncoder), content_type='text/html; charset=utf-8')


class AjaxFileUploader(object):
    def __init__(self, backend=None, **kwargs):
        if backend is None:
            backend = LocalUploadBackend
        self.get_backend = lambda: backend(**kwargs)

    def __call__(self, request, *args, **kwargs):
        return self._ajax_upload(request, *args, **kwargs)

    def _ajax_upload(self, request, *args, **kwargs):
        if request.method == "POST":
            filename = False
            headerValues = headers.initGlobals(request)
            if request.is_ajax() and False:
                # the file is stored raw in the request
                upload = request
                is_raw = True
                # AJAX Upload will pass the filename in the querystring if it
                # is the "advanced" ajax upload
                try:
                    filename = request.POST['qqfilename']
                except KeyError:
                    return HttpResponseBadRequest("AJAX request not valid")
            # not an ajax upload, so it was the "basic" iframe version with
            # submission via form
            else:
                is_raw = False
                if len(request.FILES) == 1:
                    # FILES is a dictionary in Django but Ajax Upload gives
                    # the uploaded file an ID based on a random number, so it
                    # cannot be guessed here in the code. Rather than editing
                    # Ajax Upload to pass the ID in the querystring, observe
                    # that each upload is a separate request, so FILES should
                    # only have one entry. Thus, we can just grab the first
                    # (and only) value in the dict.
                    upload = request.FILES.values()[0]
                else:
                    raise Http404("Bad Upload")

                if u'qqfilename' in request.POST:
                    filename = request.POST[u'qqfilename']
                else:
                    filesReq = request.FILES.getlist('qqfile')

                    if filesReq:
                        filesReq = filesReq[0]

                        filename = filesReq.name

            if not filename:
                return HttpResponse('Not filename found')

            backend = self.get_backend()

            # custom filename handler
            if u'qqpartindex' not in request.POST or request.POST[u'qqpartindex'] == '0':
                kwargs['first_part'] = True
            else:
                kwargs['first_part'] = False

            filename_origin = filename

            project_id = headerValues['CURRENT_PROJECT'].id if headerValues['CURRENT_PROJECT'] and headerValues[
                'CURRENT_PROJECT'].id else None
            if project_id:
                backend.UPLOAD_DIR = 'projects/' + str(project_id)

            filename = (backend.update_filename(request, filename, *args, **kwargs)
                        or filename)

            # save the file

            backend.setup(filename, *args, **kwargs)

            success = backend.upload(upload, filename, is_raw, *args, **kwargs)

            # callback
            extra_context = backend.upload_complete(request, filename, *args, **kwargs)

            # let Ajax Upload know whether we saved it or not
            ret_json = {'success': success, 'filename': filename}
            if extra_context is not None:
                ret_json.update(extra_context)

            if u'qqpartindex' in request.POST and int(request.POST[u'qqpartindex']) == int(
                    request.POST[u'qqtotalparts']) - 1:

                fileNow = PM_Files(projectId=headerValues['CURRENT_PROJECT'], authorId=request.user,
                                   name=filename_origin)
                try:
                    sId = int(request.POST.get('section_id', 0))
                except ValueError:
                    sId = 0

                version_of = int(request.POST.get('version_of', 0))

                if sId:
                    try:
                        fileNow.category = PM_File_Category.objects.get(pk=sId)
                    except PM_File_Category.DoesNotExist:
                        pass

                fileNow.file.name = os.path.join(ret_json['path'])
                if PM_Files.objects.filter(projectId_id=fileNow.projectId, name=fileNow.name, double=False,attach=False):
                    for el in PM_Files.objects.filter(projectId_id=fileNow.projectId, name=fileNow.name, double=False,attach=False):
                        if el.category_id and fileNow.file.size == el.file.size:
                            fileNow.double = True
                            ret_json.update({
                                'double': True,
                            })

                fileNow.save()

                if version_of:
                    try:
                        fileOld = PM_Files.objects.get(pk=int(version_of))
                        fileOld.addNewVersion(fileNow)
                    except PM_Files.DoesNotExist:
                        pass

                ret_json.update({
                    'id': fileNow.id,
                    'name': fileNow.name,
                    'src': fileNow.src,
                    'is_picture': fileNow.isPicture,
                    'type': fileNow.type,
                    'date_create': fileNow.date_create,
                    'size': fileNow.size,
                    'thumbnail': protected(thumbnail(str(fileNow), '167x167')) if fileNow.isPicture else ''
                })
                # although "application/json" is the correct content type, IE throws a fit
            return HttpResponse(json.dumps(ret_json, cls=DjangoJSONEncoder), content_type='text/html; charset=utf-8')

        else:
            response = HttpResponseNotAllowed(['POST'])
            response.write("ERROR: Only POST allowed")
            return response
