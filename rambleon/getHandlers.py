from django.http import Http404
from datetime import datetime as dt
from models import *
import geography
import string
from django.utils.html import escape

def dehydrateRoutesList(bundle):
	favList = bundle.obj.favourites.all()
	favCount = favList.count()
	bundle.data['favCount'] = favCount

	if favCount < 1:
			bundle.data['fav'] = False
	else:
		for i in favList:
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['fav'] = True
				break
			else:
				bundle.data['fav'] = False

	doneList = bundle.obj.doneIts.all()
	doneCount = doneList.count()
	bundle.data['doneCount'] = doneCount

	if doneCount < 1:
		bundle.data['done'] = False
	else:
		for i in doneList:
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['done'] = True
				break
			else:
				bundle.data['done'] = False

	keyList = bundle.obj.keywords.all()
	keyCount = keyList.count()

	if keyCount < 1:
		bundle.data['keywords'] = False
	else:
		words = []
		for i in keyList:
			words.append(i)
		bundle.data['keywords'] = words

	bundle.data['creation_date'] = bundle.data['creation_date'].strftime('%d %b %Y')
	bundle.data['update_date'] = bundle.data['update_date'].strftime('%d %b %Y')

	bundle.data.pop('resource_uri')

	return bundle

def dehydrateSingleRoute(bundle):
	favList = bundle.obj.favourites.all()
	favCount = favList.count()
	bundle.data['favCount'] = favCount

	if favCount < 1:
			bundle.data['fav'] = False
	else:
		for i in favList:
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['fav'] = True
				break
			else:
				bundle.data['fav'] = False

	doneList = bundle.obj.doneIts.all()
	doneCount = doneList.count()
	bundle.data['doneCount'] = doneCount

	if doneCount < 1:
		bundle.data['done'] = False
	else:
		for i in doneList:
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['done'] = True
				break
			else:
				bundle.data['done'] = False
	
	keyList = bundle.obj.keywords.all()
	keyCount = keyList.count()

	if keyCount < 1:
		bundle.data['keywords'] = False
	else:
		words = []
		for i in keyList:
			words.append(i)
		bundle.data['keywords'] = words


	if bundle.obj.pathpoints.all().count() < 1:
		bundle.data['pathpoints'] = False

	bundle.data['creation_date'] = bundle.data['creation_date'].strftime('%d %b %Y')
	bundle.data['update_date'] = bundle.data['update_date'].strftime('%d %b %Y')

	bundle.data.pop('resource_uri')

	return bundle

def dehydrateImage(bundle):
	bundle.data['creationDate'] = bundle.data['creationDate'].strftime('%d %b %Y')
	bundle.data['updateDate'] = bundle.data['updateDate'].strftime('%d %b %Y')
	return bundle

def dehydrateNote(bundle):
	bundle.data['creationDate'] = bundle.data['creationDate'].strftime('%d %b %Y')
	bundle.data['updateDate'] = bundle.data['updateDate'].strftime('%d %b %Y')
	return bundle

def dehydrateTrackData(bundle):
	bundle.data['dateRecorded'] = bundle.data['dateRecorded'].strftime('%d %m %Y %H %M %S')
	return bundle


def routesWithinBounds(routes, boundsString):
	return geography.routesWithinBounds(routes, geography.getCoordsFromBounds(boundsString))

def notesWithinBounds(notes, boundsString):
	return geography.notesWithinBounds(notes, geography.getCoordsFromBounds(boundsString))

def filterRouteKeywords(routes, keywordString):
	keywords = string.split(keywordString, ',')
	for k in keywords:
		k=k.lower()
	routes = routes.filter(keywords__keyword__in=keywords)

	return routes


#prevent injection attacks by escaping html elements before return
def escapeBundle(bundle):
	if not isinstance(bundle, Http404):
		return escapeDict(bundle.data)
	return bundle

def escapeDict(inp):
	for key in inp:
		if isinstance(inp[key], basestring):
			inp[key] = escape(inp[key])
		#elif isinstance(inp[key], dict):
			#inp[key] = escapeDict(inp[key])
		elif isinstance(inp[key], list):
			if not key == 'pathpoints':
				newList = []
				for s in inp[key]:
					newList.append(escape(s))
				inp[key] = newList
	return inp

