from django.contrib.syndication.views import Feed
from .models import Post
from django.template.defaultfilters import truncatewords

class LatestPostsFeeds(Feed):
    title = 'my blog'
    link = '/blog/'
    description = 'latest posts of of blog'

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.body, 30)
