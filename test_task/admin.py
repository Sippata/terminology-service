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


admin.site.register(HandbookItem)