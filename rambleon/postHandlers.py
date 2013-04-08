"""
Post requests from the client are processed in these functions.  They primarily deal with the 
extraction of data from the post body, and creation/manipulation of database objects

"""

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

#send a bundle off to be sanitized and return sanitized version
def sanitizeInput(bundle):
	bundle.data = getHandlers.escapeDict(bundle.data)
	return bundle

#process new registrations
def handleRegister(bundle):
	#get info from posted data
	username = bundle.data.get('user')
	email = bundle.data.get('email')
	#generate password hash
	pwHash = auth.encryptPass(bundle.data.get('passw'), username)
	#check for pre-existing username/email
	if User.objects.filter(username__iexact=username).count() != 0:
		raise Http404('Username aleady in use')
	if User.objects.filter(email__iexact=email).count() != 0:
		raise Http404('Email aleady in use')
	#make account
	try:
		newUser = User.objects.create(username=username, email=email, pwHash=pwHash, lastLogin=dt.now())
		bundle.obj = newUser
	except Exception:
		raise Http404('An error occurred when creating the account')

	return bundle

#handle new route creation
def handleNewRoute(bundle):
	#get info from posted data
	private = bundle.data.get('private') == True
	name = bundle.data.get('name')
	keywords = bundle.data.get('keywords')
	pathpoints = bundle.data.get('pathpoints')
	mapThumbnail = bundle.data.get('mapThumbnail')

	#find user posting route
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	#make route
	newRoute = Route(user=user, name=name, private=private, mapThumbnail=mapThumbnail)
	newRoute.save()

	#add keywords to route
	addKeywords(keywords=keywords, route=newRoute)
	#add pathpoints to route
	addPathPoints(pathpoints=pathpoints, route=newRoute)

	#assign bundle's object to be route, required if api is set to always return data
	bundle.obj = newRoute
	return bundle

#used to update a route
def updateRoute(bundle):
	#get info from posted data
	routeID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		#get route object
		route = Route.objects.get(pk=routeID)
	except Exception:
		raise Http404('Invalid Route')

	#make sure user owns route, and update any provided data
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
	#save changes
	route.save()
	#update bundle
	bundle.obj=route
	return bundle

def deleteRoute(bundle):
	#get info from posted data
	routeID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		#get route
		route = Route.objects.get(pk=routeID)
	except Exception:
		raise Http404('Invalid Route')

	#if user owns route delete it, else complain
	if route.user == user:
		route.delete()
	else:
		raise Http404('You do not own this Route')

	return bundle

#add keywords by creating keyword objects and assigning them to a route
def addKeywords(keywords, route):
	for k in keywords:
		#conver to lowercase
		k=k.lower()
		try:
			#look for existing object with this keyword
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

#create a new pathpoint object for each one submitted
def addPathPoints(pathpoints, route):
	i = 0
	for p in pathpoints:
		PathPoint.objects.create(route=route, orderNum=i, lat=Decimal(p['lat']), lng=Decimal(p['lng']))
		i += 1

#create a new note
def handleNewNote(bundle):
	#get info from posted data
	title = bundle.data.get('title')
	private = bundle.data.get('private') == True
	lat = bundle.data.get('lat')
	lng = bundle.data.get('lng')
	content = bundle.data.get('content')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))

	#make note
	newNote = Note(title=title, user=user, lat=lat, lng=lng, private=private, content=content)
	#save note
	newNote.save()
	#assign note to bundle
	bundle.obj = newNote
	return bundle

#update a note
def updateNote(bundle):
	#get posted data
	noteID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		#find note from ID
		note = Note.objects.get(pk=noteID)
	except Exception:
		raise Http404('Invalid Note')

	#if user owns note in question, update supplied info
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

	#save changes
	note.save()
	bundle.obj = note
	return bundle

#deletes a note from the system
def deleteNote(bundle):
	#get posted data
	noteID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		#find note
		note = Note.objects.get(pk=noteID)
	except Exception:
		raise Http404('Invalid Note')

	#delete if user owns note
	if note.user == user:
		note.delete()
	else:
		raise Http404('You do not own this Note')


	return bundle

#create a new image
def handleNewImage(bundle):
	#get posted data
	title = bundle.data.get('title')
	private = bundle.data.get('private') == True
	lat = bundle.data.get('lat')
	lng = bundle.data.get('lng')
	text = bundle.data.get('text')
	image = bundle.data.get('image')
	thumbnail = bundle.data.get('thumbnail')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))

	#create image object
	newImage = Image(user=user, title=title, private=private, lat=lat, lng=lng, text=text, image=image, thumbnail=thumbnail)
	#save it
	newImage.save()
	#update bundle with new object
	bundle.obj = newImage
	return bundle

#update an image object
def updateImage(bundle):
	#get posted data
	imageID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		#find image
		image = Image.objects.get(pk=imageID)
	except Exception:
		raise Http404('Invalid Image')

	#update image with any supplied data
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

	#save changes
	image.save()
	#update bundle object
	bundle.obj = image
	return bundle

#delete an image object
def deleteImage(bundle):
	#get posted data
	imageID = bundle.data.get('id')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))

	try:
		#find image
		image = Image.objects.get(pk=imageID)
	except Exception:
		raise Http404('Invalid Image')
	#if user owns image, delete image
	if image.user == user:
		image.delete()
	else:
		raise Http404('You do not own this Image')

	return bundle

#delete a user object, this requires a password check 
def deleteAccount(bundle):
	#get posted data
	passw = bundle.data.get('passw')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	#check hash of password matches the one stored, and delete accordingly
	if user.pwHash == auth.encryptPass(passw, user.username):
		user.delete()
	else:
		raise Http404('Invalid Username or Password')

	return bundle

#update an account's details, requires password check
def updateAccount(bundle):
	#get posted data
	passw = bundle.data.get('passw')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	#check hash of supplied password against the one stored
	#update supplied data accordingly
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

	#save changes
	user.save()
	#update bundle object
	bundle.obj = user
	return bundle

#reset password by receiving a code sent to the user's email.
def resetPassword(bundle):
	#get posted data
	passw = bundle.data.get('newpassw')
	code = bundle.data.get('code')
	try:
		#check if code matches against user
		userObj = AuthLinkCode.objects.get(code=code).user
	except Exception:
		raise Http404('Invalid reset code')

	#use supplied new password to generate new pw hash
	userObj.pwHash = auth.encryptPass(passw, userObj.username)
	#save changes
	userObj.save()
	#update bundle object
	bundle.obj = userObj
	return bundle

#set a route to 'done' for a given user, or undo the done record.
def doneIt(bundle):
	#get posted data
	routeID = bundle.data.get('route')
	boolean = bundle.data.get('set')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		#find route
		route = Route.objects.get(pk=routeID)
	except Exception:
		raise Http404('Invalid Route')

	try:
		#look for this doneit already existing, by examining user's current done records
		existing = DoneIt.objects.all().filter(user=user).get(route=route)
		#delete existing record if 'set' is set to false by the client
		if not boolean:
			existing.delete()
	except Exception:
		#no record found, 
		if boolean:
			#create new record if 'set' is set to true by the client
			newDoneIt = DoneIt(user=user, route=route, date=dt.now())
			newDoneIt.save()
		else:
			raise Http404('DoneIt record does not exist')

	return bundle

#set a route to 'favourite' for a given user, or undo the favourite record.
def favourite(bundle):
	#get posted data
	routeID = bundle.data.get('route')
	boolean = bundle.data.get('set')
	user = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	try:
		#find route
		route = Route.objects.get(pk=routeID)
	except Exception:
		raise Http404('Invalid Route')

	try:
		#look for this favourite already existing, by examining user's current done records
		existing = Favourite.objects.all().filter(user=user).get(route=route)
		#delete existing record if 'set' is set to false by the client
		if not boolean:
			existing.delete()
	except Exception:
		#no record found
		if boolean:
			#create new record if 'set' is set to true by the client
			newFav = Favourite(user=user, route=route, date=dt.now())
			newFav.save()
		else:
			raise Http404('Favourite record does not exist')

	return bundle

#send an email to the requesting user containing a code which they can use to reset their password via the website
def forgotPassword(bundle):
	try:
		#find user from post request
		userObj = User.objects.get(username__iexact=bundle.data.get('user'))
	except Exception:
		raise Http404('Username does not Exist')

	#create new reset code object, using the API Key generator (will be a different hash due to different current system time)
	newCode = AuthLinkCode(user=userObj, code=auth.genApiKey(userObj.username))
	newCode.save()

	#create email string
	emailStr = 'Dear ' + userObj.username + ',\n\n'
	emailStr += 'We have received a request to reset your Ramble Online password.\n\n'
	emailStr += 'Please visit the following link to reset your password:\n'
	emailStr += 'http://www.rambleonline.com/resetPassword.html?code=' + newCode.code+'\n\n'
	emailStr += 'If you did not request this email, there is no need to do anything.\n\n'
	emailStr += 'Regards,\nRamble Online Support'

	#send email with django.core.send_mail function, using SMTP settings from the settings.py file in ./server/
	try:
		send_mail('Ramble Online Password Reset Request', emailStr, 'support@rambleonline.com',
	 [userObj.email], fail_silently=False)
	except Exception:
		raise Http404('Email could not be sent at this time, please try later')

	bundle.obj = userObj

	return bundle

#add a speed track data record
def addTrackData(bundle):
	try:
		#get posted info
		userObj = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	except Exception:
		raise Http404('Username does not Exist')

	#create and save new object
	newItem = SpeedTrackData(user=userObj, dateRecorded=dt.now(), speed=Decimal(bundle.data.get('speed')), altitude=bundle.data.get('altitude'))
	newItem.save()

	bundle.obj = newItem

	return bundle

#send an email to a supplied email address on behalf of the requesting user.  this called once per email to share with
def shareRoute(bundle):
	try:
		userObj = User.objects.get(username__iexact=bundle.request.GET.get('user'))
	except Exception:
		raise Http404('Username does not Exist')

	#create email text
	emailStr = 'Hi, ' + bundle.data.get('recipient')+'\n\n'
	emailStr += 'Ramble Online user \'' + userObj.username + '\' has suggested you try out a route!\n'
	emailStr += userObj.username + ' says: ' + bundle.data.get('message') + '\n\n'

	emailStr += 'Access the route via the following link:\n'
	emailStr += 'http://www.rambleonline.com/route.html?ref=external&id='+bundle.data.get('route') + ' \n'
	emailStr += 'Please note you will have to log in in order to see the route.\n\n'

	emailStr += 'Please do not reply to this email, you may contact the sender\nusing their supplied email address: ' + userObj.email + '\n\n'

	emailStr += 'Happy Rambling, \nthe Ramble Online team.\nhttp://www.rambleonline.com'

	#send email with django.core.send_mail function, using SMTP settings from the settings.py file in ./server/
	try:
		send_mail('Ramble Online: '+userObj.username+' has shared a route with you', emailStr, 'support@rambleonline.com',
	 [bundle.data.get('email')], fail_silently=False)
	except Exception:
		raise Http404('Email to ' + bundle.data.get('email') +' could not be sent at this time, please try later')

	bundle.obj = userObj
	return bundle
