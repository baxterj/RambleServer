from django.http import Http404
from datetime import datetime as dt
from models import *
import string
from decimal import *
import auth

#Methods here should take a tastypie bundle
#they should return the modified bundle or 
#raise a Http404('error description')

def handleRegister(bundle):
	
	username = bundle.data.get('user')
	email = bundle.data.get('email')
	pwHash = auth.encryptPass(bundle.data.get('passw'), username)
	if User.objects.filter(username__iexact=username).count() != 0:
		raise Http404('Username aleady in use')
	if User.objects.filter(email__iexact=email).count() != 0:
		raise Http404('Email aleady in use')
	try:
		newUser = User.objects.create(username=username, email=email, pwHash=pwHash, lastLogin=dt.now())
		bundle.obj = newUser
	except Exception:
		raise Http404('An error occurred when creating the account')

	return bundle

def handleNewRoute(bundle):
	
	private = bundle.data.get('private') == True
	name = bundle.data.get('name')
	keywords = bundle.data.get('keywords')
	pathpoints = bundle.data.get('pathpoints')
	mapThumbnail = bundle.data.get('mapThumbnail')

	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	newRoute = Route(user=user, name=name, private=private, mapThumbnail=mapThumbnail)
	newRoute.save()

	addKeywords(keywords=keywords, route=newRoute)
	addPathPoints(pathpoints=pathpoints, route=newRoute)

	bundle.obj = newRoute
	return bundle


def updateRoute(bundle):
	routeID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		route = Route.objects.get(pk=routeID)
	except Exception:
		raise Http404('Invalid Route')

	if route.user == user:
		if bundle.data.get('private') != None:
			route.private = bundle.data.get('private') == True

		if bundle.data.get('name') != None:
			route.name = bundle.data.get('name')

		if bundle.data.get('mapThumbnail') != None:
			route.mapThumbnail = bundle.data.get('mapThumbnail')

		if bundle.data.get('pathpoints') != None:
			PathPoint.objects.filter(route=route).delete()
			addPathPoints(pathpoints=bundle.data.get('pathpoints'), route=route)

		if bundle.data.get('keywords') != None:
			HasKeyword.objects.filter(route=route).delete()
			addKeywords(keywords=bundle.data.get('keywords'), route=route)

	else:
		raise Http404('You do not own this route')

	route.save()
	bundle.obj=route
	return bundle

def deleteRoute(bundle):
	routeID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		route = Route.objects.get(pk=routeID)
	except Exception:
		raise Http404('Invalid Route')

	if route.user == user:
		route.delete()
	else:
		raise Http404('You do not own this Route')

	return bundle

def addKeywords(keywords, route):
	for k in keywords:
		k=k.lower()
		try:
			stored = Keyword.objects.get(keyword__iexact=k)
		except Exception:
			stored = None
		if stored != None:
			#use existing keyword
			HasKeyword.objects.create(keyword=stored, route=route)
		else:
			#make new keyword
			newWord = Keyword.objects.create(keyword=k)
			HasKeyword.objects.create(keyword=newWord, route=route)

def addPathPoints(pathpoints, route):
	i = 0
	for p in pathpoints:
		PathPoint.objects.create(route=route, orderNum=i, lat=Decimal(p['lat']), lng=Decimal(p['lng']))
		i += 1


def handleNewNote(bundle):
	title = bundle.data.get('title')
	private = bundle.data.get('private') == True
	lat = bundle.data.get('lat')
	lng = bundle.data.get('lng')
	content = bundle.data.get('content')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))

	newNote = Note(title=title, user=user, lat=lat, lng=lng, private=private, content=content)
	newNote.save()

	bundle.obj = newNote
	return bundle

def updateNote(bundle):
	noteID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		note = Note.objects.get(pk=noteID)
	except Exception:
		raise Http404('Invalid Note')

	if note.user == user:
		if bundle.data.get('title') != None:
			note.title = bundle.data.get('title')
		
		if bundle.data.get('private') != None:
			note.private = bundle.data.get('private') == True

		if bundle.data.get('lat') != None:
			note.lat = bundle.data.get('lat')

		if bundle.data.get('lng') != None:
			note.lng = bundle.data.get('lng')

		if bundle.data.get('content') != None:
			note.lng = bundle.data.get('content')

	else:
		raise Http404('You do not own this note')


	note.save()
	bundle.obj = note
	return bundle

def deleteNote(bundle):
	noteID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		note = Note.objects.get(pk=noteID)
	except Exception:
		raise Http404('Invalid Note')

	if note.user == user:
		note.delete()
	else:
		raise Http404('You do not own this Note')


	return bundle

def handleNewImage(bundle):
	title = bundle.data.get('title')
	private = bundle.data.get('private') == True
	lat = bundle.data.get('lat')
	lng = bundle.data.get('lng')
	text = bundle.data.get('text')
	image = bundle.data.get('image')
	thumbnail = bundle.data.get('thumbnail')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))

	newImage = Image(user=user, title=title, private=private, lat=lat, lng=lng, text=text, image=image, thumbnail=thumbnail)
	newImage.save()

	bundle.obj = newImage
	return bundle

def updateImage(bundle):
	imageID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		image = Image.objects.get(pk=imageID)
	except Exception:
		raise Http404('Invalid Image')

	if image.user == user:
		if bundle.data.get('title') != None:
			image.title = bundle.data.get('title')

		if bundle.data.get('image') != None:
			image.image = bundle.data.get('image')

		if bundle.data.get('thumbnail') != None:
			image.thumbnail = bundle.data.get('thumbnail')

		if bundle.data.get('text') != None:
			image.text = bundle.data.get('text')
		
		if bundle.data.get('private') != None:
			image.private = bundle.data.get('private') == True

		if bundle.data.get('lat') != None:
			image.lat = bundle.data.get('lat')

		if bundle.data.get('lng') != None:
			image.lng = bundle.data.get('lng')


	else:
		raise Http404('You do not own this image')


	image.save()
	bundle.obj = image
	return bundle


def deleteImage(bundle):
	imageID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		image = Image.objects.get(pk=imageID)
	except Exception:
		raise Http404('Invalid Image')

	if image.user == user:
		image.delete()
	else:
		raise Http404('You do not own this Image')

	return bundle

def deleteAccount(bundle):
	passw = bundle.data.get('passw')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	if user.pwHash == passw:
		user.delete()
	else:
		raise Http404('Invalid Username or Password')

	return bundle

def updateAccount(bundle):
	passw = bundle.data.get('passw')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	if user.pwHash == passw:
		if bundle.data.get('email') != None:
			user.email = bundle.data.get('email')
		if bundle.data.get('newpassw') != None:
			user.pwHash = bundle.data.get('newpassw')
	else:
		raise Http404('Invalid Username or Password')

	user.save()
	bundle.obj = user
	return bundle

def doneIt(bundle):
	routeID = bundle.data.get('route')
	boolean = bundle.data.get('set')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		route = Route.objects.get(pk=routeID)
	except Exception:
		raise Http404('Invalid Route')

	try:
		existing = DoneIt.objects.all().filter(user=user).get(route=route)
		if boolean == False:
			existing.delete()
	except Exception:
		if boolean == True:
			newDoneIt = DoneIt(user=user, route=route, date=dt.now())
			newDoneIt.save()
		else:
			raise Http404('DoneIt record does not exist')

	return bundle

def favourite(bundle):
	routeID = bundle.data.get('route')
	boolean = bundle.data.get('set')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		route = Route.objects.get(pk=routeID)
	except Exception:
		raise Http404('Invalid Route')

	try:
		existing = Favourite.objects.all().filter(user=user).get(route=route)
		if not boolean:
			existing.delete()
	except Exception:
		if boolean:
			newFav = Favourite(user=user, route=route, date=dt.now())
			newFav.save()
		else:
			raise Http404('Favourite record does not exist')

	return bundle