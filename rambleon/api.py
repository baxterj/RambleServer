from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authentication import Authentication
from rambleon.models import Route, PathPoint, User, ApiKeys
from auth import getKey

class RouteResource(ModelResource):
	pathpoints = fields.ToManyField('rambleon.api.PathPointResource', 'pathpoints', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name='route'

class PathPointResource(ModelResource):
	route = fields.ToOneField('rambleon.api.RouteResource', 'route')
	class Meta:
		queryset = PathPoint.objects.all()
		resource_name = 'pathpoint'

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'

class ApiKeysResource(ModelResource):
	class Meta:
		queryset = ApiKeys.objects.all()
		detail_allowed_methods = ['get']
		resource_name='apikeys'
		limit = 1

	def dehydrate(self, bundle):
		bundle.data = {}
		bundle.data['key'] = getKey(bundle.request.GET.get('user'))
		return bundle