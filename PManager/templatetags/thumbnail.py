# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
import os
from PIL import Image
from django.template import Library
from tracker import settings

register = Library()

@register.filter(name='thumbnail')
def thumbnail(file, size='200x200', resample=0):
    # defining the size
    x, y = [int(x) for x in size.split('x')]
    # defining the filename and the miniature filename
    basename, format = file.rsplit('.', 1)
#    print basename
    miniature = basename + '_' + size + '.' +  format
    miniature = miniature.replace('media/', 'media/thumbnails/')
    if not miniature.startswith('media/'):
        miniature = 'media/' + miniature

    if not miniature.startswith('/'):
        miniature = '/' + miniature

    miniature_filename = 'tracker' + miniature
    miniature_url = str(miniature)
    if not miniature_url.startswith('/'):
        miniature_url = '/' + miniature_url

    miniature_dir = miniature_filename.split('/')
    del(miniature_dir[-1])
    miniature_dir = '/'.join(miniature_dir)
    # if the image wasn't already resized, resize it

    if not os.path.exists(miniature_filename):
        # todo: fix all upload paths to be general
        if not file.startswith('media'):
            file = os.path.join('media', file)
        if file.startswith('/'):
            filename = 'tracker' + file
        else:
            filename = os.path.join('tracker', file)
        print str(filename)
        if os.path.isfile(filename):
            try:
                if not os.path.exists(miniature_dir):
                    os.makedirs(miniature_dir)

                image = Image.open(filename)
                image.thumbnail([x, y], resample) # generate a 200x200 thumbnail
                image.save(miniature_filename, image.format)
            except IOError:
                return file

    return miniature_url

@register.filter(name='protected')
def protected(url):
    if url.startswith('/'):
        url = url[1:]
    return os.path.join('/protected', str(url))
