from organizations.models import Organization, Category
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class CategoryOptions(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Category, CategoryOptions)
admin.site.register(Organization)

