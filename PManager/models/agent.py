__author__ = 'Gvammer'
from django.db import models
import datetime, json

class Agent(models.Model):
    datetime = models.DateTimeField(null=True, blank=True)
    seconds = models.IntegerField(null=True, blank=True)
    method = models.CharField(max_length=500)
    required = models.CharField(max_length=500, null=True, blank=True)
    once = models.BooleanField(blank=True)
    last_result_message = models.CharField(max_length=1000, null=True, blank=True)
    last_process_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.method

    def process(self):
        result = False
        # try:
        if self.required:
            exec('import ' + self.required)

        exec('result = ' + self.method)
        if self.once:
            self.delete()
        else:
            self.datetime = datetime.datetime.now() + datetime.timedelta(seconds=self.seconds)
            self.last_result_message = json.dumps(result)
            self.last_process_date = datetime.datetime.now()
            self.save()
        # except Exception:
        #     pass

        return result

    @staticmethod
    def addAgent(func, time, interval):
        agent = Agent(
            method=func,
            datetime=time,
            seconds=interval
        )
        agent.save()
        return agent


    class Meta:
        app_label = 'PManager'