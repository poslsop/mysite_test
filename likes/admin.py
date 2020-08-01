from django.contrib import admin
from .models import LikeRecord, LikeCount
# Register your models here.
@admin.register(LikeRecord)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('user', 'liked_time', 'content_object')
@admin.register(LikeCount)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'liked_num')
