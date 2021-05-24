import datetime
from django.utils import timezone


class WorkTime(object):
    taskHours = 0
    taskRealTime = 0
    startDateTime = None
    endDateTime = None
    startWorkDay = 10
    endWorkDay = 19
    holyDays = [6, 7]

    def __init__(self, *args, **kargs):
        if 'userHoursPerDay' in kargs and kargs['userHoursPerDay']:
            self.endWorkDay = self.startWorkDay + int(kargs['userHoursPerDay'])

        if 'taskHours' in kargs and 'startDateTime' in kargs and kargs['taskHours'] and kargs['startDateTime']:
            self.taskHours = kargs['taskHours']

            try:
                self.startDateTime = timezone.make_aware(kargs['startDateTime'], timezone.get_default_timezone())
            except ValueError:
                self.startDateTime = kargs['startDateTime']

            self.taskRealTime = self.cropHolyDays()
            self.endDateTime = self.startDateTime + datetime.timedelta(hours=self.taskRealTime)

    def getTimeBetween(self, startDate, endDate, hoursPerDay=None):
        endWorkDay = self.endWorkDay

        if hoursPerDay is not None:
            if hoursPerDay > 23:
                hoursPerDay = 23

            endWorkDay = self.startWorkDay + hoursPerDay

        if endWorkDay > 23:
            endWorkDay = 23

        allTime = 0

        if any((startDate is None, endDate is None)):
            return allTime

        while self.isHolyday(startDate.isoweekday()) or startDate.hour >= endWorkDay:
            startDate += datetime.timedelta(days=1)
            startDate = datetime.datetime(startDate.year, startDate.month, startDate.day, self.startWorkDay, 0, 0,  0, startDate.tzinfo)

        while self.isHolyday(endDate.isoweekday()) or endDate.hour < self.startWorkDay:
            endDate -= datetime.timedelta(days=1)
            endDate = datetime.datetime(endDate.year, endDate.month, endDate.day, endWorkDay, 0, 0,  0, endDate.tzinfo)

        if startDate.hour < self.startWorkDay:
            startDate = datetime.datetime(startDate.year, startDate.month, startDate.day, self.startWorkDay, 0, 0,  0, startDate.tzinfo)

        if endDate > datetime.datetime(endDate.year, endDate.month, endDate.day, endWorkDay, 0, 0,  0, endDate.tzinfo):
            endDate = datetime.datetime(endDate.year, endDate.month, endDate.day, endWorkDay, 0, 0,  0, endDate.tzinfo)

        if startDate.minute > 0:
            allTime += round(float(60 - startDate.minute) / 60.0, 2)

            startDate += datetime.timedelta(hours=1)
            startDate = datetime.datetime(startDate.year, startDate.month, startDate.day, startDate.hour, 0, 0,  0, startDate.tzinfo)

        if endDate.minute > 0:
            allTime += round(float(startDate.minute) / 60.0, 2)

            endDate -= datetime.timedelta(hours=1)
            endDate = datetime.datetime(endDate.year, endDate.month, endDate.day, endDate.hour, 0, 0,  0, endDate.tzinfo)

        if startDate.hour >= endWorkDay:
            startDate += datetime.timedelta(days=1)
            startDate = datetime.datetime(startDate.year, startDate.month, startDate.day, self.startWorkDay, 0, 0,  0, startDate.tzinfo)

        while startDate < endDate:
            if not self.isHolyday(startDate.isoweekday()):
                allTime += 1

            startDate += datetime.timedelta(hours=1)
            if startDate.hour >= endWorkDay:
                startDate += datetime.timedelta(days=1)
                startDate = datetime.datetime(startDate.year, startDate.month, startDate.day, self.startWorkDay, 0, 0,  0, startDate.tzinfo)

        return allTime

    def isHolyday(self, day):
        return day in self.holyDays

    def cropHolyDays(self):
        allTime = 0
        curHour = 0
        curDay = 0
        iterations = 0
        timeLength = self.taskHours
        if not self.holyDays:
            self.holyDays = [6, 7]

        if timeLength > 0:
            while curHour < timeLength and iterations < 1000:
                iterations = iterations + 1

                allTime = self.startDateTime.hour + curHour
                curDay = (self.startDateTime + datetime.timedelta(hours=curHour)).isoweekday()

                if allTime > 24:
                    allTime %= 24

                if self.isHolyday(curDay):
                    hoursToEndOfDay = 24 - allTime
                    timeLength += hoursToEndOfDay
                    curHour += hoursToEndOfDay

                    # and next day
                    timeLength += 1
                    curHour += 1
                    continue

                if (allTime >= self.endWorkDay) or (allTime < self.startWorkDay):
                    timeLength += 1

                curHour += 1

        return curHour
