from django.contrib import admin
from django.utils.html import format_html

from .models import Rules


class RulesAdmin(admin.ModelAdmin):
    list_display = ['url', 'image_tag']

    def image_tag(self, obj):
        return format_html('<a href="{}">{}</a>'.format(obj.image.url, obj.image))

    image_tag.short_description = 'Image'


admin.site.register(Rules, RulesAdmin)
