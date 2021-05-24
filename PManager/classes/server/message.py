__author__ = 'Gvammer'
import json

class ServerMessage(object):
    type = ''
    objectName = ''
    fields = None
    id = None

    def __init__(self, *args, **kwargs):
        if 'connection' in kwargs \
            and 'fields' in kwargs \
            and 'type' in kwargs:

            self.conn = kwargs['connection']
            self.fields = kwargs['fields']
            self.type = kwargs['type']
            self.objectName = kwargs['objectName'] if 'objectName' in kwargs else 'task'
            self.id = kwargs['id'] if 'id' in kwargs else None
        else:
            raise Exception('Bad message fields')

    def send(self):
        if self.canAccess():
            self.setAdditionalFields()
            result = self.fields
            channel = '.'.join(['fs', self.objectName, self.type])

            self.conn.send(channel, result)

    @staticmethod
    def getFromPMMessage(message, connection):
        pass

    @staticmethod
    def getFromRedisMessage(redisMessage, connection):
        type = None
        objectName = None
        messageFromJson = json.loads(redisMessage.body)
        channel = redisMessage.channel.split('.')

        if 'onlyForUsers' in messageFromJson:
            if not connection.user or connection.user.id not in messageFromJson['onlyForUsers']:
                return False

        if channel:
            type = channel.pop()
        if channel:
            objectName = channel.pop()

        message = None
        if type and objectName:
            newMessageFields = {
                'connection': connection,
                'fields': messageFromJson,
                'type': type,
                'objectName': objectName,
                'id': messageFromJson.get('id', None)
            }

            if objectName == 'task':
                message = TaskMessage(**newMessageFields)
            elif objectName == 'comment':
                message = CommentMessage(**newMessageFields)

        if message:
            return message
        else:
            print 'Undefined message channel from redis', redisMessage.channel
            return False

class TaskMessage(ServerMessage):
    def canAccess(self):
        return True

    def setAdditionalFields(self):
        self.fields['id'] = self.id

class CommentMessage(ServerMessage):
    comment = None

    def __init__(self, *args, **kwargs):
        from PManager.models.tasks import PM_Task_Message
        ServerMessage.__init__(self, *args, **kwargs)
        self.comment = PM_Task_Message.objects.get(id=self.id)

    def canAccess(self):
        return self.comment.canView(self.conn.user)

    def setAdditionalFields(self):
        self.fields.update(self.comment.getJson(None, self.conn.user))

class RedisMessage():
    def __init__(self, redis_queue, objectName='task', type='update', fields=None):
        self.queue = redis_queue

        self.objectName = objectName
        self.type = type
        self.fields = fields if fields else {}

    def send(self):
        channel = '.'.join(['re', self.objectName, self.type])
        self.queue(channel, json.dumps(self.fields))