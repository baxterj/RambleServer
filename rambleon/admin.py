from rambleon.models import *
from django.contrib import admin

class PointInline(admin.TabularInline):
	model = PathPoint
	extra = 2

class RouteKeywordInline(admin.TabularInline):
	model = HasKeyword
	extra = 2

class RoutesAdmin(admin.ModelAdmin):
	inlines = [PointInline, RouteKeywordInline]
	list_display = ('name', 'creation_date', 'update_date')

admin.site.register(Route, RoutesAdmin)

class UserFaveInline(admin.TabularInline):
	model = Favourite
	extra = 2

class UserDoneInline(admin.TabularInline):
	model = DoneIt
	extra = 2

class UserAdmin(admin.ModelAdmin):
	inlines = [UserFaveInline, UserDoneInline]
	list_display = ('username', 'email', 'pwHash', 'lastLogin')
	readonly_fields = ('regDate',)

admin.site.register(User, UserAdmin)

class KeywordAdmin(admin.ModelAdmin):
	list_display = ('keyword',)

admin.site.register(Keyword, KeywordAdmin)

class NoteAdmin(admin.ModelAdmin):
	list_display = ('user', 'lat', 'lng', 'private', 'content')

admin.site.register(Note, NoteAdmin)

class ImageAdmin(admin.ModelAdmin):
	list_display = ('user', 'lat', 'lng', 'private', 'text', 'image', 'thumbnail')

admin.site.register(Image, ImageAdmin)

class SpeedTrackDataAdmin(admin.ModelAdmin):
	list_display = ('user', 'secondsElapsed', 'distanceTravelled')

admin.site.register(SpeedTrackData, SpeedTrackDataAdmin)

class ApiKeysAdmin(admin.ModelAdmin):
	list_display = ('user', 'key')

admin.site.register(ApiKeys, ApiKeysAdmin)