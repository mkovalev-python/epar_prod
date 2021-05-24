# -*- coding:utf-8 -*-
__author__ = 'Rayleigh'
import urllib
import urllib2
import json
from tracker.settings import DOCKER_HOST, DOCKER_APP_KEY
from PManager.models.interfaces import AccessInterface

def server_request(project):
  result = __server_request_raw(project, '/container/start')
  if 'status' not in result or result['status'] != "OK":
    raise RuntimeError('Result is not acceptable')
  if 'mysql_password' in result and 'host' in result:
    AccessInterface.create_mysql_interface(password=result['mysql_password'], project=project, host=result['host'])
  return True


def __get_project_api_key(project):
  if not project.api_key:
    data = urllib.urlencode({'app_key' : DOCKER_APP_KEY, 'project': project.repository})
    url = "http://" + DOCKER_HOST + "/container/key"
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    result = json.load(response)
    api_key = result['API_KEY']
    project.api_key = api_key
    project.save()
    return api_key
  return project.api_key

def __server_request_raw(project, service_url):
  if not project.repository:
    raise AttributeError("repository for project is not found")
  api_key = __get_project_api_key(project)
  data = urllib.urlencode({'app_key' : DOCKER_APP_KEY, 'project': project.repository, 'api_key': api_key})
  url = "http://" + DOCKER_HOST + service_url
  req = urllib2.Request(url, data)
  response = urllib2.urlopen(req)
  result = json.load(response)
  return result

def server_status_request(project):
  result = __server_request_raw(project, '/container/status')
  if 'status' not in result or result['status'] != "UP":
    return False
  return True
