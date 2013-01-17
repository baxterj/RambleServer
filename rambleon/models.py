from django.db import models
from django.utils import timezone
import datetime


class User(models.Model):
	username = models.CharField(max_length=20, unique=True)
	email = models.EmailField(max_length=254, unique=True)
	pwHash = models.CharField(max_length=40)
	regDate = models.DateTimeField(auto_now_add=True)
	lastLogin = models.DateTimeField(blank=False)	

	def __unicode__(self):
		return self.username

class Keyword(models.Model):
	keyword = models.CharField(max_length=30)

	def __unicode__(self):
		return self.keyword

class Route(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(max_length=200)
	creation_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField('last updated', auto_now=True)
	private = models.BooleanField()
	mapThumbnail = models.TextField(blank=True)
	keywords = models.ManyToManyField(Keyword, through='HasKeyword', related_name='routeKeywords')
	favourites = models.ManyToManyField(User, through='Favourite', related_name='favouriteRoutes')
	doneIts = models.ManyToManyField(User, through='DoneIt', related_name='doneRoutes')

	def __unicode__(self):
		return self.name

class PathPoint(models.Model):
	route = models.ForeignKey(Route, related_name='pathpoints')
	orderNum = models.IntegerField()
	lat = models.DecimalField(max_digits=10, decimal_places=6)
	lng = models.DecimalField(max_digits=10, decimal_places=6)

	def __unicode__(self):
		return str(self.orderNum)

class Favourite(models.Model):
	user = models.ForeignKey(User)
	route = models.ForeignKey(Route)
	date = models.DateTimeField('set at', auto_now_add=True)

class DoneIt(models.Model):
	user = models.ForeignKey(User)
	route = models.ForeignKey(Route)
	date = models.DateTimeField('set at', auto_now_add=True)

class HasKeyword(models.Model):
	keyword = models.ForeignKey(Keyword)
	route = models.ForeignKey(Route)

class Note(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField(max_length=60)
	content = models.TextField()
	creationDate = models.DateTimeField(auto_now_add=True)
	updateDate = models.DateTimeField(auto_now=True)
	lat = models.DecimalField(max_digits=10, decimal_places=6)
	lng = models.DecimalField(max_digits=10, decimal_places=6)
	private = models.BooleanField()

	def __unicode__(self):
		return str(self.user) + ' at ' + str(self.lat) + ':' + str(self.lng)

class Image(models.Model):
	user = models.ForeignKey(User)
	title = models.CharField(max_length=60)
	image = models.TextField(blank=True)
	thumbnail = models.TextField(blank=True)
	text = models.TextField()
	creationDate = models.DateTimeField(auto_now_add=True)
	updateDate = models.DateTimeField(auto_now=True)
	lat = models.DecimalField(max_digits=10, decimal_places=6)
	lng = models.DecimalField(max_digits=10, decimal_places=6)
	private = models.BooleanField()

	def __unicode__(self):
		return str(self.user) + ' at ' + str(self.lat) + ':' + str(self.lng)

class SpeedTrackData(models.Model):
	user = models.ForeignKey(User)
	dateRecorded = models.DateTimeField(auto_now_add=True)
	speed = models.DecimalField(max_digits=6, decimal_places=2)
	altitude = models.DecimalField(max_digits=6, decimal_places=2)

	def __unicode__(self):
		return str(self.user) + ' on ' + str(self.dateRecorded)

class ApiKeys(models.Model):
	user = models.ForeignKey(User)
	key = models.CharField(max_length=64)

class AuthLinkCode(models.Model):
	user = models.ForeignKey(User)
	code = models.CharField(max_length=40)