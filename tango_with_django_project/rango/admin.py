from django.contrib import admin
from rango.models import Page, Category, UserProfile

class PageAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'url', 'views')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'views', 'likes')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)