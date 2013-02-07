from django.http import Http404
from datetime import datetime as dt
from models import *
import string
from decimal import *
import auth
from django.core.mail import send_mail
import getHandlers

#Methods here should take a tastypie bundle
#they should return the modified bundle or 
#raise a Http404('error description')

def sanitizeInput(bundle):
	bundle.data = getHandlers.escapeDict(bundle.data)
	return bundle

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
	if user.pwHash == auth.encryptPass(passw, user.username):
		user.delete()
	else:
		raise Http404('Invalid Username or Password')

	return bundle

def updateAccount(bundle):
	passw = bundle.data.get('passw')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	if user.pwHash == auth.encryptPass(passw, user.username):
		if bundle.data.get('email') != None:
			if User.objects.filter(email__iexact=bundle.data.get('email')).count() != 0:
				raise Http404('Email aleady in use')
			else:
				user.email = bundle.data.get('email')
		if bundle.data.get('newpassw') != None:
			user.pwHash = auth.encryptPass(bundle.data.get('newpassw'), user.username)
	else:
		raise Http404('Invalid Username or Password')

	user.save()
	bundle.obj = user
	return bundle

def resetPassword(bundle):
	passw = bundle.data.get('newpassw')
	code = bundle.data.get('code')
	try:
		userObj = AuthLinkCode.objects.get(code=code).user
	except Exception:
		raise Http404('Invalid reset code')

	userObj.pwHash = auth.encryptPass(passw, userObj.username)
	userObj.save()
	bundle.obj = userObj
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

def forgotPassword(bundle):
	try:
		userObj = User.objects.get(username__iexact=bundle.data.get('user'))
	except Exception:
		raise Http404('Username does not Exist')

	newCode = AuthLinkCode(user=userObj, code=auth.genApiKey(userObj.username))
	newCode.save()

	emailStr = 'Dear ' + userObj.username + ',\n\n'
	emailStr += 'We have received a request to reset your Ramble Online password.\n\n'
	emailStr += 'Please visit the following link to reset your password:\n'
	emailStr += 'http://www.rambleonline.com/resetPassword.html?code=' + newCode.code+'\n\n'
	emailStr += 'If you did not request this email, there is no need to do anything.\n\n'
	emailStr += 'Regards,\nRamble Online Support'

	try:
		send_mail('Ramble Online Password Reset Request', emailStr, 'support@rambleonline.com',
	 [userObj.email], fail_silently=False)
	except Exception:
		raise Http404('Email could not be sent at this time, please try later')

	bundle.obj = userObj

	return bundle

def addTrackData(bundle):
	try:
		userObj = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	except Exception:
		raise Http404('Username does not Exist')

	newItem = SpeedTrackData(user=userObj, dateRecorded=dt.now(), speed=Decimal(bundle.data.get('speed')), altitude=bundle.data.get('altitude'))
	newItem.save()

	bundle.obj = newItem

	return bundle

def shareRoute(bundle):
	try:
		userObj = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	except Exception:
		raise Http404('Username does not Exist')

	emailStr = 'Hi, ' + bundle.data.get('recipient')+'\n\n'
	emailStr += 'Ramble Online user \'' + userObj.username + '\' has suggested you try out a route!\n'
	emailStr += userObj.username + ' says: ' + bundle.data.get('message') + '\n\n'

	emailStr += 'Access the route via the following link:\n'
	emailStr += 'http://www.rambleonline.com/route.html?ref=external&id='+bundle.data.get('route') + ' \n'
	emailStr += 'Please note you will have to log in in order to see the route.\n\n'

	emailStr += 'Please do not reply to this email, you may contact the sender\nusing their supplied email address: ' + userObj.email + '\n\n'

	emailStr += 'Happy Rambling, \nthe Ramble Online team.\nhttp://www.rambleonline.com'

	try:
		send_mail('Ramble Online: '+userObj.username+' has shared a route with you', emailStr, 'support@rambleonline.com',
	 [bundle.data.get('email')], fail_silently=False)
	except Exception:
		raise Http404('Email to ' + bundle.data.get('email') +' could not be sent at this time, please try later')

	bundle.obj = userObj
	return bundle
