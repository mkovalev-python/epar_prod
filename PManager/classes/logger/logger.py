__author__ = 'Gvammer'

class Logger(object):
    modelClass = False
    def __init__(self, modelClass=None):
        if modelClass:
            self.modelClass = modelClass
        else:
            from PManager.models import LogData
            self.modelClass = LogData

    def log(self, user, type, value, project_id=None):
        data = self.modelClass(code=type, value=value, user=user, project_id=project_id)
        data.save()
        return data