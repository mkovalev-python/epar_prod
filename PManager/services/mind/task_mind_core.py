__author__ = 'Gvammer'
from pybrain.datasets import SupervisedDataSet
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure import TanhLayer
from pybrain.supervised.trainers import BackpropTrainer
from PManager.models import PM_Task, LogData
import pickle, os
from scipy import stats

class TaskMind:
    _instance = None
    _threshold = 100.00
    _net = None
    _container = os.path.dirname(os.path.realpath(__file__)) + '/Hodor.brain'

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaskMind, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if os.path.isfile(self._container):
            fileObj = open(self._container, 'rb')
            self._net = pickle.load(fileObj)
            fileObj.close()
        else:
            self._net = buildNetwork(6, 14, 1, hiddenclass=TanhLayer)
            self.save()

    def getInputParams(self, task):
        similar = PM_Task.getSimilar(task.name+(task.text or u''), task.project)

        if task.resp and len(similar):
            f = lambda x: 1 if (float(x) / self._threshold) > 1 else (float(x) / self._threshold)

            similarQty = len(similar)

            a = []
            similarQtyUser = 0
            similarTimeUser = 0
            similarTime = 0

            for t in similar:
                task_time = float(t.getAllTime()) / 3600.
                if task_time <= 0: task_time = 0.1

                a.append(task_time)
                if t.resp and task.resp.id == t.resp.id:
                    similarQtyUser += 1
                    similarTimeUser += task_time
            if a:
                similarTime = stats.gmean(a)

            if similarQtyUser:
                similarTimeUser = float(similarTimeUser) / float(similarQtyUser)

            timeUser = 0
            for l in LogData.objects.raw(
                    'SELECT SUM(`value`) as summ, id, user_id from PManager_logdata WHERE `user_id`=' +
                            str(int(task.resp.id)) + '' +
                    ' AND code = \'DAILY_TIME\''
                ):
                timeUser += l.summ if l.summ else 0
            timeUser = float(timeUser) / 3600.
            tasksUserQty = PM_Task.objects.filter(resp=task.resp, realDateStart__isnull=False).count()
            if tasksUserQty:
                timeUser = timeUser / float(tasksUserQty)

            from PManager.services.rating import get_user_quality_for_task
            user_quality = get_user_quality_for_task(task, task.resp)

            return (
                f(similarQty),
                f(similarTime),
                f(similarQtyUser),
                f(similarTimeUser),
                f(timeUser),
                user_quality
            )

        return False

    def check(self, task):
        setIn = self.getInputParams(task)
        if setIn:
            res = self._net.activate(list(setIn))
            if res:
                return abs(round(res[0], 2))

        return 0

    def train(self, tasks):
        ds = SupervisedDataSet(6, 1)
        for task in tasks:
            setIn = self.getInputParams(task)

            if setIn:
                time = float(task.getAllTime()) / 3600.
                time = time / self._threshold
                if time > 1:
                    time = 1

                ds.addSample(setIn, (time,))
        if (len(ds)):
            trainer = BackpropTrainer(self._net, ds)
            for i in range(100):
                trainer.train()

            self.save()

    def save(self):
        fileObj = open(self._container, 'wb')
        pickle.dump(self._net, fileObj, 2.0)
        fileObj.close()
