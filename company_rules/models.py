
from django.db import models


class Rules(models.Model):
    url = models.CharField(max_length=200)
    image = models.ImageField(upload_to='company_rules')

    def str(self):
        return self.url
