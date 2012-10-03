from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class Route(models.Model):
	name = models.CharField(max_length=200)
	creation_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField('last updated', auto_now=True)

	def __unicode__(self):
        return self.name

class PathPoint(models.Model):
	route = models.ForeignKey(Route)
	orderNum = models.IntegerField()
	lat = models.DecimalField(max_digits=10, decimal_places=5)
	lng = models.DecimalField(max_digits=10, decimal_places=5)

	def __unicode__(self):
        return self.route + '::' + self.orderNum