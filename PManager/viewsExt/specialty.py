__author__ = 'Alwx'
from django.http import HttpResponse
from PManager.models import Specialty, Tags
from django.contrib.auth.models import User
import json


def specialty_ajax(request):
    action = request.POST['action']
    response = ''
    if action == 'specialty_search':
        response = search_specialty(request)
    return HttpResponse(json.dumps(response))

def search_specialty(request):
    search_text = request.POST['search_text'].upper()
    userId = request.POST['user']
    profile_specialties = None
    if userId:
        user = User.objects.get(id=userId)
        profile = user.get_profile()
        profile_specialties = profile.specialties.all()

    specialties = Specialty.objects.filter(name__icontains=search_text)

    if profile_specialties:
        specialties = specialties.exclude(pk__in=profile_specialties)

    specialties = specialties.values_list('name', flat=True)
    return list(specialties)

def matchSpecialtyWithTags(arSpecialty):
    if arSpecialty:
        tags = Tags.objects.filter(tagText__in=arSpecialty).values('id', 'tagText', 'objectLinks')
        result = {}
        if tags:
            for tag in tags:
                result[tag['id']] = tag['tagText']
        return result
