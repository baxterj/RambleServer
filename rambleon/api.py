"""
The API file contains resources, and authentication/authorization information

"""
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from rambleon.models import *
from auth import *
import postHandlers
import getHandlers
from string import *
from decimal import *

#quick switch for enabling input sanitization. turn off mostly for debugging
sanitizeInput = True

#Standard authentication method for ramble online. checks api key against username in auth module
class MyApiKeyAuthentication(Authentication):
	def is_authenticated(self, request, **kwargs):
		return validKey(name=request.GET.get('user'), key=request.GET.get('apikey'))

#allows everyone, use sparingly
class MyLoginAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

#authorize user to only access their own records. used in account-based tasks such as route sharing and editing accounts
class MyUserAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

	def apply_limits(self, request, object_list):
		if request:
			return object_list.filter(username__iexact=request.GET.get('user'))
		else:
			return object_list.none()

#manipulate the authorization mechanic to return routes applicable to the user. 
#includes routes belonging to the user as well as those by others marked as 'favourite' or 'done'.  
#private routes belonging to others are excluded
class MyRoutesAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True
		
	def apply_limits(self, request, object_list):
		if request:
			my = object_list.filter(user__username__iexact=request.GET.get('user'))
			fav = object_list.filter(favourites__username__iexact=request.GET.get('user'))
			done = object_list.filter(doneIts__username__iexact=request.GET.get('user'))
			#remove private routes, private done/favourites owned by user will still show from being 
			#in the 'my' list
			fav = fav.filter(private=False)
			done = done.filter(private=False)
			return (my | fav | done).distinct()
		else:
			return object_list.none()

#manipulate authorization to return all routes accessible to the user, used for the route search feature
#keyword filtering is applied (if parameters provided), map viewport bounds filtering is also applied
class MyRouteAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

	def apply_limits(self, request, object_list):
		if request:
			my = object_list.filter(user__username__iexact=request.GET.get('user'))
			others = object_list.exclude(user__username__iexact=request.GET.get('user'))
			others = others.filter(private=False) #remove private routes from list of others' routes
			routes = (my | others).distinct()
			if request.GET.get('filterwords') != None:
				routes = getHandlers.filterRouteKeywords(routes, request.GET.get('filterwords'))
			if request.GET.get('bounds') != None:
				routes = getHandlers.routesWithinBounds(routes, request.GET.get('bounds'))
			return routes
		else:
			return object_list.none()

#allow updating of resources provided the username of the attached user object matches the request
class MyUpdateAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

	def apply_limits(self, request, object_list):
		if request:
			return object_list.filter(user__username__iexact=request.GET.get('user'))
		else:
			return object_list.none()

#set up resource for routes with all pathpoints included
class RouteResource(ModelResource):
	#explicity order pathpoints by order number as they are in reverse by default
	pathpoints = fields.ToManyField('rambleon.api.PathPointResource', full=True,
		attribute=lambda bundle: bundle.obj.pathpoints.all().order_by('orderNum'))
	#get owner details
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	#get keywords list 
	keywords = fields.ToManyField('rambleon.api.KeywordResource', 'keywords', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name ='route'
		authentication = MyApiKeyAuthentication()
		authorization = MyRouteAuthorization()
		max_limit=30
		list_allowed_methods = ['get', 'post',]
		always_return_data = True

	#prepare bundle to return to client after GET request
	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateSingleRoute(bundle=bundle))

	#process post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)

		return postHandlers.handleNewRoute(bundle)

#resource for searching routes by location
class SearchRouteResource(ModelResource):
	#select only the first pathpoint, for displaying the route location on the map
	pathpoints = fields.ToManyField('rambleon.api.PathPointResource', full=True,
		attribute=lambda bundle: bundle.obj.pathpoints.filter(orderNum=0))
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	keywords = fields.ToManyField('rambleon.api.KeywordResource', 'keywords', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name ='searchroute'
		authentication = MyApiKeyAuthentication()
		authorization = MyRouteAuthorization()
		max_limit=30
		list_allowed_methods = ['get',]
		always_return_data = True

	#prepare search results bundle for sending back to client
	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateSingleRoute(bundle=bundle))


#get a list of routes for the my routes/favourite routes/done routes lists
#does not include pathpoints
class MyRoutesResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	fav = fields.ToManyField('rambleon.api.FavouriteResource', 'favourites', full=True)
	done = fields.ToManyField('rambleon.api.DoneItResource', 'doneIts', full=True)
	keywords = fields.ToManyField('rambleon.api.KeywordResource', 'keywords', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name ='myroutes'
		list_allowed_methods = ['get',]
		authentication = MyApiKeyAuthentication()
		authorization = MyRoutesAuthorization()

	#prepare bundle for sending back to client
	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateRoutesList(bundle=bundle))

#resource for updating a route
class UpdateRouteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	keywords = fields.ToManyField('rambleon.api.KeywordResource', 'keywords', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name='updateroute'
		list_allowed_methods=['post',]
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()

	#process post request
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.updateRoute(bundle)

#resource for deleting a route
class DeleteRouteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name='deleteroute'
		list_allowed_methods=['post',]
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()

	#process post request
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.deleteRoute(bundle)

#resource for keywords, not used explicitly by client, but included in route resources
class KeywordResource(ModelResource):
	class Meta:
		queryset = Keyword.objects.all()
		resource_name = 'keyword'
		authentication = MyApiKeyAuthentication()

#resource for favourites, not used explicitly by client, but included in route resources
class FavouriteResource(ModelResource):
	class Meta:
		queryset = Favourite.objects.all()
		resource_name = 'favourite'
		excludes = ['date',]
		authentication = MyApiKeyAuthentication()

#resource for doneIts, not used explicitly by client, but included in route resources
class DoneItResource(ModelResource):
	class Meta:
		queryset = Favourite.objects.all()
		resource_name = 'doneit'
		excludes = ['date',]
		authentication = MyApiKeyAuthentication()

#resource for pathpoints, not used explicitly by client, but included in route resources
class PathPointResource(ModelResource):
	route = fields.ToOneField('rambleon.api.RouteResource', 'route')
	class Meta:
		queryset = PathPoint.objects.all()
		resource_name = 'pathpoint'
		authentication = MyApiKeyAuthentication()

	#present pathpoint in concise way to reduce data volume
	def dehydrate(self, bundle):
		bundle.data = {
			'lat': bundle.data.get('lat'),
			'lng': bundle.data.get('lng'),
			'orderNum': bundle.data.get('orderNum')
		}
		return bundle

#resource for users. all info fields are removed except username for privacy
class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		authentication = MyApiKeyAuthentication()
		fields = ['username',]

	def dehydrate(self, bundle):
		#removes the resource_uri field, as it would elude to the rest of the user's data
		bundle.data.pop('resource_uri')
		return getHandlers.escapeBundle(bundle)

#resource for handling share route requests. User is used as the queryset as the user's email address is looked up
class ShareRouteResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'shareroute'
		authentication = MyApiKeyAuthentication()
		authorization = MyUserAuthorization()
		list_allowed_methods = ['post',]
		fields = ['username',]

	#process post request
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.shareRoute(bundle)

#user's account details, more info available here, but still not password
class AccountResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'account'
		authentication = MyApiKeyAuthentication()
		authorization = MyUserAuthorization()
		fields = ['username', 'email', 'regDate',]
		list_allowed_methods = ['get',]

	#prepare bundle for sending back to client
	def dehydrate(self, bundle):
		bundle.data.pop('resource_uri') 
		return getHandlers.escapeBundle(bundle)

#resource for updating user accounts. No field restrictions here but post only, so security is not compromised
class UpdateAccountResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'updateaccount'
		authentication = MyApiKeyAuthentication()
		authorization = MyUserAuthorization()
		list_allowed_methods = ['post',]

	#process post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.updateAccount(bundle)

#resource for deleting accounts. No field restrictions here but post only, so security is not compromised
class DeleteAccountResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'deleteaccount'
		authentication = MyApiKeyAuthentication()
		authorization = MyUserAuthorization()
		fields = ['username',]
		list_allowed_methods = ['post',]

	#process post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.deleteAccount(bundle)

#resource for accessing API keys, aka logging in.
class ApiKeysResource(ModelResource):
	class Meta:
		queryset = ApiKeys.objects.all()
		resource_name='login'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return bundle #do nothing, but need to override method so nothing happens..

	#login checking is done in the dehydrate stage
	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(checkLogin(bundle))

#resource for processing new user registrations
class RegistrationResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'register'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	#process post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.handleRegister(bundle)

	#login checking done here, which returns a new API key to the client
	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(checkLogin(bundle))

#resource for receiving lost password requests. 
class ForgotPasswordResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'forgotpassword'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	#handle post requests, in this case sends an email
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.forgotPassword(bundle)

	#return confirmation of success
	def dehydrate(self, bundle):
		bundle.data = {
			'message': 'Email sent to: ' + bundle.obj.email
		}
		return getHandlers.escapeBundle(bundle)

#resource for acting on reset password requests, using the reset code
class ResetPasswordResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'resetpassword'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	#return confirmation, including reminder of username
	def dehydrate(self, bundle):
		bundle.data = {
			'message': 'Password for: ' + bundle.obj.username + ' reset successfully'
		}
		return getHandlers.escapeBundle(bundle)

	#handle post request
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.resetPassword(bundle)

#use authorization to select notes or images that a user can see. 
#private items are removed if owned by others
#map viewport bounds filtering is carried out
class MyNoteImageAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

	def apply_limits(self, request, object_list):
		if request:
			my = object_list.filter(user__username__iexact=request.GET.get('user'))
			others = object_list.exclude(user__username__iexact=request.GET.get('user'))
			others = others.filter(private=False) #remove private routes from list of others' routes
			notes = (my | others).distinct()
			#implement this for note searching if decide to do in future
			# if request.GET.get('filterwords') != None:
			# 	routes = getHandlers.filterRouteKeywords(routes, request.GET.get('filterwords'))
			if request.GET.get('bounds') != None:
				notes = getHandlers.notesWithinBounds(notes, request.GET.get('bounds'))
			return notes
		else:
			return object_list.none()

#resource for viewing and creating notes
class NoteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Note.objects.all()
		resource_name='note'
		authentication = MyApiKeyAuthentication()
		authorization = MyNoteImageAuthorization()
		list_allowed_methods=['get','post',]
		max_limit=30
		always_return_data = True

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.handleNewNote(bundle)

	#return requested information to client
	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateNote(bundle))

#resource for updating notes
class UpdateNoteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Note.objects.all()
		resource_name='updatenote'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.updateNote(bundle)

#resource for deleting notes
class DeleteNoteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Note.objects.all()
		resource_name='deletenote'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.deleteNote(bundle)

#resource for creating and viewing images
class ImageResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Image.objects.all()
		resource_name='image'
		authentication = MyApiKeyAuthentication()
		authorization = MyNoteImageAuthorization()
		list_allowed_methods=['get','post',]
		max_limit=30
		always_return_data = True

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.handleNewImage(bundle)

	#return requested data to client
	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateImage(bundle))

#resource for updating images
class UpdateImageResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Image.objects.all()
		resource_name='updateimage'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.updateImage(bundle)

#resource for deleting images
class DeleteImageResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Note.objects.all()
		resource_name='deleteimage'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.deleteImage(bundle)

#resource for updating doneit records
class UpdateDoneItResource(ModelResource):
	user = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = DoneIt.objects.all()
		resource_name = 'done'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.doneIt(bundle)

#resource for updating favourite records
class UpdateFavouriteResource(ModelResource):
	user = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = DoneIt.objects.all()
		resource_name = 'fav'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.favourite(bundle)

#resource for creating and accessing Track Data records
class TrackDataResource(ModelResource):
	class Meta:
		queryset = SpeedTrackData.objects.all().order_by('id')
		resource_name = 'trackdata'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods = ['get', 'post',]
		max_limit = None
		limit = 0

	#handle post requests
	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.addTrackData(bundle)

	#prepare track data for sending back to client
	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateTrackData(bundle))