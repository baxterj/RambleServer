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

sanitizeInput = True


class MyApiKeyAuthentication(Authentication):
	def is_authenticated(self, request, **kwargs):
		return validKey(name=request.GET.get('user'), key=request.GET.get('apikey'))

 #USE FOR LOGIN ONLY, allows everyone
class MyLoginAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

class MyUserAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

	def apply_limits(self, request, object_list):
		if request:
			return object_list.filter(username__iexact=request.GET.get('user'))
		else:
			return object_list.none()

class MyRoutesAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True
		
	def apply_limits(self, request, object_list):
		if request:
			my = object_list.filter(user__username__iexact=request.GET.get('user'))
			fav = object_list.filter(favourites__username__iexact=request.GET.get('user'))
			done = object_list.filter(doneIts__username__iexact=request.GET.get('user'))
			#remove private routes, favourites owned by user will still show from being 
			#in the 'my' list
			fav = fav.filter(private=False)
			done = done.filter(private=False)
			return (my | fav | done).distinct()
		else:
			return object_list.none()

#includes search
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

class MyUpdateAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

	def apply_limits(self, request, object_list):
		if request:
			return object_list.filter(user__username__iexact=request.GET.get('user'))
		else:
			return object_list.none()


class RouteResource(ModelResource):
	#pathpoints = fields.ToManyField('rambleon.api.PathPointResource', 'pathpoints', full=True)
	pathpoints = fields.ToManyField('rambleon.api.PathPointResource', full=True,
		attribute=lambda bundle: bundle.obj.pathpoints.all().order_by('orderNum'))
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	keywords = fields.ToManyField('rambleon.api.KeywordResource', 'keywords', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name ='route'
		authentication = MyApiKeyAuthentication()
		authorization = MyRouteAuthorization()
		max_limit=30
		list_allowed_methods = ['get', 'post',]
		always_return_data = True

	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateSingleRoute(bundle=bundle))

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)

		return postHandlers.handleNewRoute(bundle)


class SearchRouteResource(ModelResource):
	#pathpoints = fields.ToManyField('rambleon.api.PathPointResource', 'pathpoints', full=True)
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

	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateSingleRoute(bundle=bundle))

	# def obj_create(self, bundle, request=None, **kwargs):
	# 	if(sanitizeInput):
	# 		bundle = postHandlers.sanitizeInput(bundle)

	# 	return postHandlers.handleNewRoute(bundle)


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

	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateRoutesList(bundle=bundle))

class UpdateRouteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	keywords = fields.ToManyField('rambleon.api.KeywordResource', 'keywords', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name='updateroute'
		list_allowed_methods=['post',]
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.updateRoute(bundle)

class DeleteRouteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name='deleteroute'
		list_allowed_methods=['post',]
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.deleteRoute(bundle)

class KeywordResource(ModelResource):
	class Meta:
		queryset = Keyword.objects.all()
		resource_name = 'keyword'
		authentication = MyApiKeyAuthentication()

class FavouriteResource(ModelResource):
	class Meta:
		queryset = Favourite.objects.all()
		resource_name = 'favourite'
		excludes = ['date',]
		authentication = MyApiKeyAuthentication()

class DoneItResource(ModelResource):
	class Meta:
		queryset = Favourite.objects.all()
		resource_name = 'doneit'
		excludes = ['date',]
		authentication = MyApiKeyAuthentication()

class PathPointResource(ModelResource):
	route = fields.ToOneField('rambleon.api.RouteResource', 'route')
	class Meta:
		queryset = PathPoint.objects.all()
		resource_name = 'pathpoint'
		authentication = MyApiKeyAuthentication()

	def dehydrate(self, bundle):
		bundle.data = {
			'lat': bundle.data.get('lat'),
			'lng': bundle.data.get('lng'),
			'orderNum': bundle.data.get('orderNum')
		}
		return bundle

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		authentication = MyApiKeyAuthentication()
		fields = ['username',]

	def dehydrate(self, bundle):
		#removes the resource_uri field
		bundle.data.pop('resource_uri')
		return getHandlers.escapeBundle(bundle)

class ShareRouteResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'shareroute'
		authentication = MyApiKeyAuthentication()
		authorization = MyUserAuthorization()
		list_allowed_methods = ['post',]
		fields = ['username',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.shareRoute(bundle)


class AccountResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'account'
		authentication = MyApiKeyAuthentication()
		authorization = MyUserAuthorization()
		fields = ['username', 'email', 'regDate',]
		list_allowed_methods = ['get',]

	def dehydrate(self, bundle):
		bundle.data.pop('resource_uri') 
		return getHandlers.escapeBundle(bundle)

class UpdateAccountResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'updateaccount'
		authentication = MyApiKeyAuthentication()
		authorization = MyUserAuthorization()
		list_allowed_methods = ['post',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.updateAccount(bundle)



class DeleteAccountResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'deleteaccount'
		authentication = MyApiKeyAuthentication()
		authorization = MyUserAuthorization()
		fields = ['username',]
		list_allowed_methods = ['post',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.deleteAccount(bundle)

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

	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(checkLogin(bundle))

class RegistrationResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'register'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.handleRegister(bundle)

	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(checkLogin(bundle))

class ForgotPasswordResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'forgotpassword'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.forgotPassword(bundle)

	def dehydrate(self, bundle):
		bundle.data = {
			'message': 'Email sent to: ' + bundle.obj.email
		}
		return getHandlers.escapeBundle(bundle)

class ResetPasswordResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'resetpassword'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	def dehydrate(self, bundle):
		bundle.data = {
			'message': 'Password for: ' + bundle.obj.username + ' reset successfully'
		}
		return getHandlers.escapeBundle(bundle)

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.resetPassword(bundle)


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

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.handleNewNote(bundle)

	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateNote(bundle))

class UpdateNoteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Note.objects.all()
		resource_name='updatenote'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.updateNote(bundle)

class DeleteNoteResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Note.objects.all()
		resource_name='deletenote'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.deleteNote(bundle)

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

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.handleNewImage(bundle)

	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateImage(bundle))

class UpdateImageResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Image.objects.all()
		resource_name='updateimage'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.updateImage(bundle)

class DeleteImageResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = Note.objects.all()
		resource_name='deleteimage'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.deleteImage(bundle)

class UpdateDoneItResource(ModelResource):
	user = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = DoneIt.objects.all()
		resource_name = 'done'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.doneIt(bundle)

class UpdateFavouriteResource(ModelResource):
	user = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	class Meta:
		queryset = DoneIt.objects.all()
		resource_name = 'fav'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods=['post',]

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.favourite(bundle)

class TrackDataResource(ModelResource):
	class Meta:
		queryset = SpeedTrackData.objects.all()
		resource_name = 'trackdata'
		authentication = MyApiKeyAuthentication()
		authorization = MyUpdateAuthorization()
		list_allowed_methods = ['get', 'post',]
		max_limit = None
		limit = 0

	def obj_create(self, bundle, request=None, **kwargs):
		if(sanitizeInput):
			bundle = postHandlers.sanitizeInput(bundle)
		return postHandlers.addTrackData(bundle)

	def dehydrate(self, bundle):
		return getHandlers.escapeBundle(getHandlers.dehydrateTrackData(bundle))