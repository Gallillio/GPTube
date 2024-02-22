from django.db import models

# Create your models here.
class React(models.Model):
    user_query = models.CharField(max_length=500)

class Books(models.Model):
    title = models.CharField(max_length=50)