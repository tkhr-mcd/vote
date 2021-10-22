from django.contrib import admin
from vote.models import Vote, Member, Comment, Image, User
# from import_export.resources import ModelResource
# from import_export.admin import ImportMixin
# from import_export.formats import base_formats


# Register your models here.
admin.site.register(Vote)
admin.site.register(Member)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Image)

