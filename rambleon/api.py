from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from rambleon.models import Route, PathPoint, User, ApiKeys
from auth import checkLogin, validKey


class MyApiKeyAuthentication(Authentication):
	def is_authenticated(self, request, **kwargs):
		return validKey(name=request.GET.get('user'), key=request.GET.get('apikey'))

 #USE FOR LOGIN ONLY, allows everyone
class MyLoginAuthorization(Authorization):
	def is_authorized(self, request, object=None):
		return True

    # Optional but recommended
    #def get_identifier(self, request):
    #    return request.user.username

class RouteResource(ModelResource):
	pathpoints = fields.ToManyField('rambleon.api.PathPointResource', 'pathpoints', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name ='route'
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

class ApiKeysResource(ModelResource):
	class Meta:
		queryset = ApiKeys.objects.all()
		list_allowed_methods = ['get',]
		resource_name='login'
		limit = 1
		authentication = Authentication()
		authorization = MyLoginAuthorization()
		#always_return_data = True

	def dehydrate(self, bundle):
		bundle.data = {}
		#bundle.data['key'] = checkLogin(bundle.request.POST)
		bundle.data['key'] = checkLogin(name='john351', passw='adgsdgdsagsg')
		#bundle.data['key'] = checkLogin(bundle.request.GET.get('user'), bundle.request.GET.get('passw'))
		return bundle



