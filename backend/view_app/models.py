from django.db import models

# Create your models here.
class React(models.Model):
    user_query = models.CharField(max_length=500)