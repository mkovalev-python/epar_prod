# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import Agreement
from django.shortcuts import HttpResponse
import datetime, json


def __show_agreement(request):
    if request.user.is_authenticated():
        id = int(request.POST.get('id', 0))
        if id:
            try:
                agreement = Agreement.objects.get(pk=id)
                return agreement.render()
            except Agreement.DoesNotExist:
                pass


def __approve_agreement(request):
    if request.user.is_authenticated():
        id = int(request.POST.get('id', 0))
        if id:
            try:
                agreement = Agreement.objects.get(pk=id)
                if request.user.id == agreement.payer.id:
                    agreement.approvedByPayer = True
                    if not agreement.datePayerApprove:
                        agreement.datePayerApprove = datetime.datetime.now()

                if request.user.id == agreement.resp.id:
                    agreement.approvedByResp = True
                    if not agreement.dateRespApprove:
                        agreement.dateRespApprove = datetime.datetime.now()

                agreement.save()

                new_agreement = Agreement.objects.filter(resp=request.user, approvedByResp=False)
                if new_agreement.exists():
                    new_agreement = new_agreement[0]
                    return json.dumps({'id': new_agreement.id, 'text': new_agreement.text})

                new_agreement = Agreement.objects.filter(payer=request.user, approvedByPayer=False)
                if new_agreement.exists():
                    new_agreement = new_agreement[0]
                    return json.dumps({'id': new_agreement.id, 'text': new_agreement.text})


                return json.dumps({})

            except Agreement.DoesNotExist:
                pass


def ajax_handler(request):
    response = ''
    action = request.POST.get('action', False)
    if action == 'show_agreement':
        response = __show_agreement(request)
    elif action == 'approve_agreement':
        response = __approve_agreement(request)

    return HttpResponse(response)