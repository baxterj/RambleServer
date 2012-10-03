from rambleon.models import Route, PathPoint
from django.contrib import admin

class PointInline(admin.TabularInline):
	model = PathPoint
	extra = 3

class RoutesAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,               {'fields': ['name']}),
		('Date information', {'fields': ['creation_date', 'update_date'], 'classes': ['collapse']}),
	]
	inlines = [PointInline]
	list_display = ('name', 'creation_date', 'update_date')

admin.site.register(Route, RoutesAdmin)