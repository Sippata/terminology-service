from django.contrib import admin

from .models import Handbook, HandbookItem


class HandbookItemInline(admin.TabularInline):
    model = HandbookItem
    extra = 1
    fields = ['code', 'content']


@admin.register(Handbook)
class HandbookAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'short_name', 'version', 'create_date']
    inlines = [HandbookItemInline]
    list_display = ['name', 'short_name', 'version', 'create_date']
    list_filter = ['name', 'version', 'create_date']
    search_fields = ['name', 'version', 'name']


admin.site.register(HandbookItem)