# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from rambleon.models import Route, PathPoint
from django.template import Context, loader
from django.core import serializers



def index(request):
	routes = Route.objects.all().order_by('-creation_date')
	return render_to_response('rambleon/index.html', {'route_list': routes})

def route(request, route_id):
	route = get_object_or_404(Route, pk=route_id)
	return render_to_response('rambleon/route.html', {'route': route})#, 'points': route.pathpoint_set().all()})
	#return render_to_response('rambleon/route.html')

def login(request):
	return render_to_response('rambleon/login.html')

def register(request):
	return render_to_response('rambleon/register.html')

def test(request):
	return render_to_response('rambleon/testCreateRoute.html')