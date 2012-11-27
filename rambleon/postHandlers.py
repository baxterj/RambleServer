from django.http import Http404
from datetime import datetime as dt
from models import *
import string
from decimal import *

#Methods here should take a tastypie bundle
#they should return the modified bundle or 
#raise a Http404('error description')

def handleRegister(bundle):
	
	username = bundle.data.get('user')
	email = bundle.data.get('email')
	pwHash = bundle.data.get('passw')
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
	for k in keywords:
		k=k.lower()
		try:
			stored = Keyword.objects.get(keyword__iexact=k)
		except Exception:
			stored = None
		if stored != None:
			#use existing keyword
			HasKeyword.objects.create(keyword=stored, route=newRoute)
		else:
			#make new keyword
			newWord = Keyword.objects.create(keyword=k)
			HasKeyword.objects.create(keyword=newWord, route=newRoute)
	i = 0
	for p in pathpoints:
		print p
		PathPoint.objects.create(route=newRoute, orderNum=i, lat=Decimal(p['lat']), lng=Decimal(p['lng']))
		i += 1


	return bundle