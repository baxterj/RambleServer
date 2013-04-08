"""
The admin file configures the admin panel for record management

"""

from rambleon.models import *
from django.contrib import admin

#Pathpoints within route page
class PointInline(admin.TabularInline):
	model = PathPoint
	extra = 1

#Leywords within route page
class RouteKeywordInline(admin.TabularInline):
	model = HasKeyword
	extra = 1

#route page
class RoutesAdmin(admin.ModelAdmin):
	inlines = [PointInline, RouteKeywordInline]
	list_display = ('name', 'user', 'creation_date', 'update_date')

admin.site.register(Route, RoutesAdmin)

#Favourites list for user page
class UserFaveInline(admin.TabularInline):
	model = Favourite
	#model = Route.favourites.through
	extra = 1

#Done list for user page
class UserDoneInline(admin.TabularInline):
	model = DoneIt
	extra = 1

#user page
class UserAdmin(admin.ModelAdmin):
	inlines = [UserFaveInline, UserDoneInline]
	list_display = ('username', 'email', 'pwHash', 'lastLogin', 'regDate')
	readonly_fields = ('regDate',)

admin.site.register(User, UserAdmin)

#keyword page
class KeywordAdmin(admin.ModelAdmin):
	list_display = ('keyword',)

admin.site.register(Keyword, KeywordAdmin)

#note page
class NoteAdmin(admin.ModelAdmin):
	list_display = ('user', 'lat', 'lng', 'private', 'title')

admin.site.register(Note, NoteAdmin)

#image page
class ImageAdmin(admin.ModelAdmin):
	list_display = ('user', 'title', 'private', 'text')

admin.site.register(Image, ImageAdmin)

#speed track data page
class SpeedTrackDataAdmin(admin.ModelAdmin):
	list_display = ('user', 'dateRecorded', 'speed', 'altitude')

admin.site.register(SpeedTrackData, SpeedTrackDataAdmin)

#api keys page
class ApiKeysAdmin(admin.ModelAdmin):
	list_display = ('user', 'key')

admin.site.register(ApiKeys, ApiKeysAdmin)

#favourite page
class FavouriteAdmin(admin.ModelAdmin):
	list_display=('user', 'route', 'date')

admin.site.register(Favourite, FavouriteAdmin)

#done it page
class DoneItAdmin(admin.ModelAdmin):
	list_display=('user', 'route', 'date')

admin.site.register(DoneIt, DoneItAdmin)

#auth link code page
class AuthLinkCodeAdmin(admin.ModelAdmin):
	list_display=('user', 'code')

admin.site.register(AuthLinkCode, AuthLinkCodeAdmin)