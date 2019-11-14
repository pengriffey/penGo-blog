from django.contrib import admin
from blog.models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title','slug','author','publish','status',)
    list_filter = ('status','created','publish','author')
    search_fields = ('title','author__username','body')
    prepopulated_fields = {'slug':('title',)}
    ordering = ('status','publish')
    # raw_id_fields = ('author',)
    date_hierarchy = 'publish'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post','body','name','email','created','active')
    search_fields = ('body','name','email')
    list_filter = ('created','active','updated',)
    ordering = ('-created',)