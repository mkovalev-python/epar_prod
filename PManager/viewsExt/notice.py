__author__ = 'Gvammer'
from django.shortcuts import HttpResponse
from PManager.models import PM_Notice

def noticeSetRead(request):
    id = request.POST.get('id', None)
    if id:
        try:
            notice = PM_Notice.objects.get(pk=id).setRead(request.user)
        except PM_Notice.DoesNotExist:
            pass
    return HttpResponse('')