from rambleon.models import Route, PathPoint
from django.contrib import admin

class PointInline(admin.TabularInline):
	model = PathPoint
	extra = 3

class RoutesAdmin(admin.ModelAdmin):
	inlines = [PointInline]
	list_display = ('name', 'creation_date', 'update_date')

admin.site.register(Route, RoutesAdmin)