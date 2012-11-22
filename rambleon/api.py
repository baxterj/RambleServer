from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from rambleon.models import *
from auth import *
from postHandlers import *
from getHandlers import *

class MyApiKeyAuthentication(Authentication):
	def is_authenticated(self, request, **kwargs):
		return validKey(name=request.GET.get('user'), key=request.GET.get('apikey'))

 #USE FOR LOGIN ONLY, allows everyone
class MyLoginAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

class MyRoutesAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True
		
	def apply_limits(self, request, object_list):
		if request:
			my = object_list.filter(user__username__iexact=request.GET.get('user'))
			fav = object_list.filter(favourites__username__iexact=request.GET.get('user'))
			done = object_list.filter(doneIts__username__iexact=request.GET.get('user'))
			print fav.count()
			return (my | fav | done).distinct()
		else:
			return object_list.none()

    # Optional but recommended
    #def get_identifier(self, request):
    #    return request.user.username

class RouteResource(ModelResource):
	pathpoints = fields.ToManyField('rambleon.api.PathPointResource', 'pathpoints', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name ='route'
		authentication = MyApiKeyAuthentication()

class MyRoutesResource(ModelResource):
	owner = fields.ToOneField('rambleon.api.UserResource', 'user', full=True)
	fav = fields.ToManyField('rambleon.api.FavouriteResource', 'favourites', full=True)
	done = fields.ToManyField('rambleon.api.DoneItResource', 'doneIts', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name ='myroutes'
		list_allowed_methods = ['get',]
		#authentication = MyApiKeyAuthentication()
		authorization = MyRoutesAuthorization()


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

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		authentication = MyApiKeyAuthentication()
		fields = ['username',]

	def dehydrate(self, bundle):
		#removes the resource_uri field
		bundle.data = {'username': bundle.data.get('username'),}
		return bundle

class ApiKeysResource(ModelResource):
	class Meta:
		queryset = ApiKeys.objects.all()
		resource_name='login'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	def obj_create(self, bundle, request=None, **kwargs):
		return bundle #do nothing, but need to override method so nothing happens..

	def dehydrate(self, bundle):
		return checkLogin(bundle)

class RegistrationResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'register'
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		list_allowed_methods = ['post',]
		always_return_data = True

	def obj_create(self, bundle, request=None, **kwargs):
		return handleRegister(bundle)

	def dehydrate(self, bundle):
		return checkLogin(bundle)