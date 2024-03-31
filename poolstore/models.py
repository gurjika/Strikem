from django.db import models

# Create your models here.


class PoolHouse(models.Model):
    title = models.CharField(max_length=255)
    
class Table(models.Model):
    reserved = models.BooleanField()
    poolhouse = models.ForeignKey(PoolHouse, on_delete=models.CASCADE, related_name='tables')


    