from django.test import TestCase
import auth
import hashlib
import geography
from models import *
from decimal import *
from datetime import datetime as dt
import getHandlers
import postHandlers

#AUTH
class TestEncryptPass(TestCase):
	def testEncryptPass(self):
		passw= 'hello123'
		username='CAts'
		h = hashlib.sha1()
		h.update('adgi43g3g' + passw + '4352fmv' + username.lower())
		self.assertEqual(auth.encryptPass(passw, username), h.hexdigest())

class TestApiKeyGen(TestCase):
#		self.testUser = User.objects.create(username='james', email='em@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())
	def testApiKeyGen(self):
		self.assertNotEqual(auth.genApiKey('james'), auth.genApiKey('james'))

class TestValidKey(TestCase):
	def testValidKey(self):
		testUser = User.objects.create(username='james', email='em@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())
		testKeyStr = 'abcdef'
		testKey = ApiKeys.objects.create(user=testUser, key='abcdef')
		self.assertTrue(auth.validKey('james', 'abcdef'))


#GEOGRAPHY
class TestRoutesWithBounds(TestCase):
	def testRoutesWithBounds(self):
		testUser = User.objects.create(username='james2', email='em2@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())

		testRoute = Route.objects.create(user=testUser, name='route 1', private=True, mapThumbnail='thumb')
		PathPoint.objects.create(route=testRoute, orderNum=0, lat=Decimal('2.000000'), lng=Decimal('2.000000'))

		testRouteTwo = Route.objects.create(user=testUser, name='route 2', private=True, mapThumbnail='thumb')
		PathPoint.objects.create(route=testRouteTwo, orderNum=0, lat=Decimal('1.000000'), lng=Decimal('1.000000'))
		
		routes = Route.objects.filter(user__username__iexact='james2')
		coords = {
			'swLat': Decimal('0.0'),
			'swLng': Decimal('0.0'),
			'neLat': Decimal('1.5'),
			'neLng': Decimal('1.5'),
		}
		
		self.assertEqual(geography.routesWithinBounds(routes, coords).count(), 1) 

class TestCoordsFromBounds(TestCase):
	def testCoordsFromBounds(self):
		coords = geography.getCoordsFromBounds('1.000000,123.112441,111.222222,123.456789')
		self.assertEqual(coords['swLat'], Decimal('1.000000'))
		self.assertEqual(coords['swLng'], Decimal('123.112441'))
		self.assertEqual(coords['neLat'], Decimal('111.222222'))
		self.assertEqual(coords['neLng'], Decimal('123.456789'))

class TestNotesWithinBounds(TestCase):
	def testNotesWithinBounds(self):
		testUser = User.objects.create(username='james2', email='em2@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())
		testNote = Note.objects.create(title='test note', user=testUser, lat='1.000000', lng='1.000000', private=True, content='this is a note')
		testNote = Note.objects.create(title='test note 2', user=testUser, lat='2.000000', lng='2.000000', private=True, content='this is a note')

		notes = Note.objects.filter(user__username__iexact='james2')
		coords = {
			'swLat': Decimal('0.0'),
			'swLng': Decimal('0.0'),
			'neLat': Decimal('1.5'),
			'neLng': Decimal('1.5'),
		}

		self.assertEqual(geography.notesWithinBounds(notes, coords).count(), 1) 


#GETHANDLERS
class TestGetRoutesWithinBounds(TestCase):
	def testGetRoutesWithinBounds(self):
		boundsString = '0.000000,0.000000,1.5,1.5'
		testUser = User.objects.create(username='james2', email='em2@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())

		testRoute = Route.objects.create(user=testUser, name='route 1', private=True, mapThumbnail='thumb')
		PathPoint.objects.create(route=testRoute, orderNum=0, lat=Decimal('2.000000'), lng=Decimal('2.000000'))

		testRouteTwo = Route.objects.create(user=testUser, name='route 2', private=True, mapThumbnail='thumb')
		PathPoint.objects.create(route=testRouteTwo, orderNum=0, lat=Decimal('1.000000'), lng=Decimal('1.000000'))

		testRouteThree = Route.objects.create(user=testUser, name='route 3', private=True, mapThumbnail='thumb')
		PathPoint.objects.create(route=testRouteThree, orderNum=0, lat=Decimal('-1.000000'), lng=Decimal('1.000000'))

		routes = Route.objects.filter(user__username__iexact='james2')

		self.assertEqual(getHandlers.routesWithinBounds(routes, boundsString).count(), 1) 

class TestGetNotesWithinBounds(TestCase):
	def testGetNotesWithinBounds(self):
		boundsString = '0.000000,0.000000,1.5,1.5'
		testUser = User.objects.create(username='james2', email='em2@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())
		testNote = Note.objects.create(title='test note', user=testUser, lat='1.000000', lng='1.000000', private=True, content='this is a note')
		testNote = Note.objects.create(title='test note 2', user=testUser, lat='2.000000', lng='2.000000', private=True, content='this is a note')

		notes = Note.objects.filter(user__username__iexact='james2')
		self.assertEqual(getHandlers.notesWithinBounds(notes, boundsString).count(), 1) 

class TestFilterRouteKeywords(TestCase):
	def testFilterRouteKeywords(self):
		testUser = User.objects.create(username='james2', email='em2@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())
		testRouteOne = Route.objects.create(user=testUser, name='route 1', private=True, mapThumbnail='thumb')
		testRouteTwo = Route.objects.create(user=testUser, name='route 2', private=True, mapThumbnail='thumb')

		newWordOne = Keyword.objects.create(keyword='testWORD')
		newWordTwo = Keyword.objects.create(keyword='test123')
		HasKeyword.objects.create(keyword=newWordOne, route=testRouteOne)
		HasKeyword.objects.create(keyword=newWordTwo, route=testRouteTwo)

		routes = Route.objects.filter(user__username__iexact='james2')

		testBothWords = getHandlers.filterRouteKeywords(routes, 'testWORD,test123')
		testOneWord = getHandlers.filterRouteKeywords(routes, 'testWORD,UnusedKeyword')
		testUnusedWord = getHandlers.filterRouteKeywords(routes, 'UnusedKeyword')

		self.assertEqual(testBothWords.count(), 2)
		self.assertEqual(testOneWord.count(), 1)
		self.assertEqual(testUnusedWord.count(), 0)


#POSTHANDLERS
class TestAddKeywords(TestCase):
	def testAddKeywords(self):
		testUser = User.objects.create(username='james2', email='em2@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())
		testRoute = Route.objects.create(user=testUser, name='route 1', private=True, mapThumbnail='thumb')

		postHandlers.addKeywords(['hot', 'dog'], testRoute)
		self.assertEqual(testRoute.keywords.all().count(), 2)

class TestAddPathpoints(TestCase):
	def testAddPathpoints(self):
		testUser = User.objects.create(username='james2', email='em2@ail.com', pwHash=auth.encryptPass('james', 'password'), lastLogin=dt.now())
		testRoute = Route.objects.create(user=testUser, name='route 1', private=True, mapThumbnail='thumb')

		pathpoints = [
			{
				'lat': Decimal('1.5'),
				'lng': Decimal('1.0'),
			},
			{
				'lat': Decimal('2'),
				'lng': Decimal('1.0'),
			},
		]

		postHandlers.addPathPoints(pathpoints, testRoute)
		self.assertTrue(testRoute.pathpoints.all().count(), 2)

