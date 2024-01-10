from django.contrib import admin
from .models import *

class VendingMachineAdmin(admin.ModelAdmin):
    readonly_fields = ['created_by', 'date_created', 'date_edited']
    list_display=['img_tag', 'id']

class PostAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']
    list_display=['img_tag', 'str_tag']

admin.site.register(VendingMachine, VendingMachineAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(ZipCode)
admin.site.register(City)
admin.site.register(Town)
