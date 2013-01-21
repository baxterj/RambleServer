from rambleon.models import *
from django.contrib import admin

class PointInline(admin.TabularInline):
	model = PathPoint
	extra = 1

class RouteKeywordInline(admin.TabularInline):
	model = HasKeyword
	extra = 1

class RoutesAdmin(admin.ModelAdmin):
	inlines = [PointInline, RouteKeywordInline]
	list_display = ('name', 'user', 'creation_date', 'update_date')

admin.site.register(Route, RoutesAdmin)

class UserFaveInline(admin.TabularInline):
	model = Favourite
	#model = Route.favourites.through
	extra = 1

class UserDoneInline(admin.TabularInline):
	model = DoneIt
	extra = 1

class UserAdmin(admin.ModelAdmin):
	inlines = [UserFaveInline, UserDoneInline]
	list_display = ('username', 'email', 'pwHash', 'lastLogin', 'regDate')
	readonly_fields = ('regDate',)

admin.site.register(User, UserAdmin)

class KeywordAdmin(admin.ModelAdmin):
	list_display = ('keyword',)

admin.site.register(Keyword, KeywordAdmin)

class NoteAdmin(admin.ModelAdmin):
	list_display = ('user', 'lat', 'lng', 'private', 'title')

admin.site.register(Note, NoteAdmin)

class ImageAdmin(admin.ModelAdmin):
	list_display = ('user', 'title', 'private', 'text')

admin.site.register(Image, ImageAdmin)

class SpeedTrackDataAdmin(admin.ModelAdmin):
	list_display = ('user', 'dateRecorded', 'speed', 'altitude')

admin.site.register(SpeedTrackData, SpeedTrackDataAdmin)

class ApiKeysAdmin(admin.ModelAdmin):
	list_display = ('user', 'key')

admin.site.register(ApiKeys, ApiKeysAdmin)

class FavouriteAdmin(admin.ModelAdmin):
	list_display=('user', 'route', 'date')

admin.site.register(Favourite, FavouriteAdmin)

class DoneItAdmin(admin.ModelAdmin):
	list_display=('user', 'route', 'date')

admin.site.register(DoneIt, DoneItAdmin)

class AuthLinkCodeAdmin(admin.ModelAdmin):
	list_display=('user', 'code')

admin.site.register(AuthLinkCode, AuthLinkCodeAdmin)