from django.http import Http404
from datetime import datetime as dt
from models import *
from string import *
from decimal import *

#coords is a dict of lat and lng making up a bounding rectangle, swLat, swLng, neLat, neLng
def routesWithinBounds(routes, coords):
	for r in routes:
		try:
			lat = r.pathpoints.get(orderNum=0).lat
			lng = r.pathpoints.get(orderNum=0).lng

			if lat < coords['swLat']: #if below bottom edge
				raise Exception
			if lat > coords['neLat']: #if above top edge
				raise Exception
			if lng < coords['swLng']: #if left of left edge
				raise Exception
			if lng > coords['neLng']: #if right of right edge
				raise Exception
		except Exception:
			routes = routes.exclude(pk=r.pk)
	return routes

def notesWithinBounds(notes, coords):
	for n in notes:
		try:
			if n.lat < coords['swLat']: #if below bottom edge
				raise Exception
			if n.lat > coords['neLat']: #if above top edge
				raise Exception
			if n.lng < coords['swLng']: #if left of left edge
				raise Exception
			if n.lng > coords['neLng']: #if right of right edge
				raise Exception
		except Exception:
			notes = notes.exclude(pk=n.pk)
	return notes


def getCoordsFromBounds(boundsString):
	coords = split(boundsString, ',')
	coords = {
		'swLat': Decimal(coords[0]),
		'swLng': Decimal(coords[1]),
		'neLat': Decimal(coords[2]),
		'neLng': Decimal(coords[3]),
	}

	return coords