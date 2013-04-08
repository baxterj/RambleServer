"""
getHandlers is where all dehydration functions are grouped. These functions are called
before data is returned to the client

"""

from django.http import Http404
from datetime import datetime as dt
from models import *
import geography
import string
from django.utils.html import escape

#prepare a list of routes for returning to the client, does not include path points
#the code in this function is applied to every route in the list
def dehydrateRoutesList(bundle):
	#get favourites objects for route
	favList = bundle.obj.favourites.all()
	favCount = favList.count()
	bundle.data['favCount'] = favCount

	#set True if User of a favourite object matches User making request
	if favCount < 1:
			bundle.data['fav'] = False
	else:
		for i in favList:
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['fav'] = True
				break
			else:
				bundle.data['fav'] = False

	#get done objects for route
	doneList = bundle.obj.doneIts.all()
	doneCount = doneList.count()
	bundle.data['doneCount'] = doneCount

	#set True if User of a Done object matches User making request
	if doneCount < 1:
		bundle.data['done'] = False
	else:
		for i in doneList:
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['done'] = True
				break
			else:
				bundle.data['done'] = False

	#Make a list of keywords, or insert 'False' if no keywords are set
	keyList = bundle.obj.keywords.all()
	keyCount = keyList.count()

	if keyCount < 1:
		bundle.data['keywords'] = False
	else:
		words = []
		for i in keyList:
			words.append(i)
		bundle.data['keywords'] = words

	#set dates to human readable format
	bundle.data['creation_date'] = bundle.data['creation_date'].strftime('%d %b %Y')
	bundle.data['update_date'] = bundle.data['update_date'].strftime('%d %b %Y')

	#remove individual resource uri to route, as it is not required
	bundle.data.pop('resource_uri')

	return bundle

#Prepare an individual route for return to the client. This includes path points
def dehydrateSingleRoute(bundle):
	#get list of favourite objects for route
	favList = bundle.obj.favourites.all()
	favCount = favList.count()
	bundle.data['favCount'] = favCount

	#mark 'False' if no favourites exist
	if favCount < 1:
			bundle.data['fav'] = False
	else:
		for i in favList:
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['fav'] = True
				break
			else:
				bundle.data['fav'] = False

	#get  list of Done objects for route
	doneList = bundle.obj.doneIts.all()
	doneCount = doneList.count()
	bundle.data['doneCount'] = doneCount

	#mark 'False' if no Dones exist
	if doneCount < 1:
		bundle.data['done'] = False
	else:
		for i in doneList:
			if i == User.objects.get(username__iexact=bundle.request.GET.get('user')):
				bundle.data['done'] = True
				break
			else:
				bundle.data['done'] = False
	
	#get keywords list for route
	keyList = bundle.obj.keywords.all()
	keyCount = keyList.count()

	#mark 'False' if no keywords assigned, else put into a list
	if keyCount < 1:
		bundle.data['keywords'] = False
	else:
		words = []
		for i in keyList:
			words.append(i)
		bundle.data['keywords'] = words

	#mark 'False' if route has no path points (shouldn't happen, but might)
	if bundle.obj.pathpoints.all().count() < 1:
		bundle.data['pathpoints'] = False

	#convert date strings to human readable format
	bundle.data['creation_date'] = bundle.data['creation_date'].strftime('%d %b %Y')
	bundle.data['update_date'] = bundle.data['update_date'].strftime('%d %b %Y')

	#remove individual resource uri, as not required
	bundle.data.pop('resource_uri')

	return bundle

#prepare image for sending to client
def dehydrateImage(bundle):
	#convert dates to human readable format
	bundle.data['creationDate'] = bundle.data['creationDate'].strftime('%d %b %Y')
	bundle.data['updateDate'] = bundle.data['updateDate'].strftime('%d %b %Y')
	return bundle

#prepare note for sending to client
def dehydrateNote(bundle):
	#convert dates to human readbale format
	bundle.data['creationDate'] = bundle.data['creationDate'].strftime('%d %b %Y')
	bundle.data['updateDate'] = bundle.data['updateDate'].strftime('%d %b %Y')
	return bundle

#prepare track data for sending to client
def dehydrateTrackData(bundle):
	#convert DateTime to format easily decipherable by client code
	bundle.data['dateRecorded'] = bundle.data['dateRecorded'].strftime('%d %m %Y %H %M %S')
	return bundle

#call to geography module for returning routes within a map viewport bounds rectangle
def routesWithinBounds(routes, boundsString):
	return geography.routesWithinBounds(routes, geography.getCoordsFromBounds(boundsString))

#call to geography module for returning notes or images within a map viewport bounds rectangle
def notesWithinBounds(notes, boundsString):
	return geography.notesWithinBounds(notes, geography.getCoordsFromBounds(boundsString))

#filter out routes not having one or more of the supplied keywords. case insensitive
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

#work through dict object escaping characters where relevant. pathpoints are ignored as their format is specific
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

