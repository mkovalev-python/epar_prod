from django.http import HttpResponse

from .models import Rules


def show_rule(request, *args, **kwargs):
    rule = Rules.objects.get(url=kwargs['url'])
    image_data = open(rule.image.path, "rb").read()
    return HttpResponse(image_data, content_type="image/jpeg")
