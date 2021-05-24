__author__ = 'Gvammer'
from PManager.widgets.chat import widget as messageList
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from PManager.viewsExt import headers
from PManager.models import PM_Task_Message
import json

def ajaxResponder(request):
    if request.user.is_authenticated():
        manager = ajaxActions(request)
        return HttpResponse(manager.process())

class ajaxActions(object):
    def __init__(self, request):
        self.request = request
        self.id = int(self.request.POST.get('id', 0))

        if 'action' in request.REQUEST:
            self.action = request.REQUEST['action']
        else:
            raise Exception('action does not exist')

    def process(self):
        if self.action != 'process' and '__' not in self.action and hasattr(self, self.action):
            return json.dumps(self.__getattribute__(self.action)())

    def send(self):
        from PManager.classes.server.message import RedisMessage
        from PManager.services.service_queue import service_queue
        message = PM_Task_Message(
            author=self.request.user,
            text=self.request.REQUEST.get('text', ''),
            project_id=int(self.request.REQUEST.get('project', '')),
        )
        if 'to' in self.request.REQUEST:
            try:
                message.userTo = User.objects.get(pk=int(self.request.REQUEST['to']))
            except User.DoesNotExist:
                pass

        message.save()

        responseJson = message.getJson()

        mess = RedisMessage(service_queue,
                            objectName='comment',
                            type='add',
                            fields=responseJson
                            )
        mess.send()

        return responseJson

    def update(self):
        message = PM_Task_Message.objects.get(pk=self.request.POST['id'])

        if message.updateFromRequestData(self.request.POST, self.request.user):
            message.modifiedBy = self.request.user
            message.save()

        return message.getJson()

    def setRead(self):
        if self.id > 0:
            try:
                message = PM_Task_Message.objects.get(pk=self.id)
                message.read = True
                message.save()
                return 'ok'

            except PM_Task_Message.DoesNotExist:
                return 'Message not found'
        else:
            messages = PM_Task_Message.objects.filter(
                userTo=self.request.user,
                read=False
            )
            for mes in messages:
                mes.read = True
                mes.save()

            return 'ok'

    def getMessages(self):
        headerValues = headers.initGlobals(self.request)
        result = messageList(self.request, headerValues)
        return result['messages']
