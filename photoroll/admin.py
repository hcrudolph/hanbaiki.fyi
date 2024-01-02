from django.contrib import admin
from .models import VendingMachine, Post, Tag

class VendingMachineAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "date_created", "date_edited"]
    list_display=["img_tag"]

class TagAdmin(admin.ModelAdmin):
    readonly_fields = ["slug"]

class PostAdmin(admin.ModelAdmin):
    readonly_fields = ["slug"]

admin.site.register(VendingMachine, VendingMachineAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
