from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#enable tastypie for RESTful interaction
from tastypie.api import Api
from rambleon.api import *

v1_api = Api(api_name='v1')
v1_api.register(RouteResource())
v1_api.register(PathPointResource())
v1_api.register(UserResource())
v1_api.register(ApiKeysResource())
v1_api.register(RegistrationResource())
v1_api.register(MyRoutesResource())
v1_api.register(FavouriteResource())
v1_api.register(DoneItResource())
v1_api.register(KeywordResource())


urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'server.views.home', name='home'),
	# url(r'^server/', include('server.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
	url(r'^$', 'rambleon.views.index'),
	url(r'^route/(?P<route_id>\d+)/$', 'rambleon.views.route'),
	url(r'^api/', include(v1_api.urls)),
	url(r'^login/', 'rambleon.views.login'),
	url(r'^register/', 'rambleon.views.register'),
	url(r'^test/', 'rambleon.views.test'),
)
