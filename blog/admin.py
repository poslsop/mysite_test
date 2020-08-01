from django.contrib import admin
from .models import BlogType, Blog
# Register your models here.

@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    #get_read_num来自Blog继承的ReadNumExpandMethod
    list_display = ('id','title', 'blog_type', 'author', 'get_read_num', 'created_time', 'last_updated_time')

