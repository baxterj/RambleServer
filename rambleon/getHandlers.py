from django.http import Http404
from datetime import datetime as dt
from models import *

def dehydrateRoutesList(bundle):
	if bundle.obj.favourites.all().count() < 1:
			bundle.data['fav'] = False
	else:
		for i in bundle.obj.favourites.all():
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['fav'] = True
				break
			else:
				bundle.data['fav'] = False

	if bundle.obj.doneIts.all().count() < 1:
		bundle.data['done'] = False
	else:
		for i in bundle.obj.doneIts.all():
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['done'] = True
				break
			else:
				bundle.data['done'] = False

	if bundle.obj.keywords.all().count() < 1:
		bundle.data['keywords'] = False
	else:
		words = []
		for i in bundle.obj.keywords.all():
			words.append(i)
		bundle.data['keywords'] = words

	bundle.data.pop('resource_uri')

	return bundle

def dehydrateSingleRoute(bundle):
	if bundle.obj.keywords.all().count() < 1:
		bundle.data['keywords'] = False
	else:
		words = []
		for i in bundle.obj.keywords.all():
			words.append(i)
		bundle.data['keywords'] = words


	if bundle.obj.pathpoints.all().count() < 1:
		bundle.data['pathpoints'] = False

	bundle.data.pop('resource_uri')

	return bundle