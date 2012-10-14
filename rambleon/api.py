from tastypie.resources import ModelResource
from tastypie import fields
from rambleon.models import Route, PathPoint

class RouteResource(ModelResource):
	pathpoints = fields.ToManyField('rambleon.api.PathPointResource', 'pathpoints', full=True)
	class Meta:
		queryset = Route.objects.all()
		resource_name='route'

class PathPointResource(ModelResource):
	#route = fields.ForeignKey(RouteResource, 'route')
	route = fields.ToOneField('rambleon.api.RouteResource', 'route')
	class Meta:
		queryset = PathPoint.objects.all()
		resource_name = 'pathpoint'
