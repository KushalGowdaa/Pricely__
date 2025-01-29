from django.db import models

# Create your models here.
class SearchQuery (models.Model):
    query = models.CharField(max_length=255)
    searched_on = models.DateTimeField(auto_now_add=True)