from django import template
from ..models import Post
from django.db.models import Count
# from django.utils.safestring import mark_safe
# import markdown


register = template.Library()

@register.inclusion_tag('latest_posts.html')
def latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}

@register.simple_tag
def most_commented_posts(count=5):
    return Post.published.annotate(num_comments=Count('comments')).order_by('num_comments')[:count]

# @register.filter(name='markdown')
# def markdown_format(text):
#     return mark_safe(markdown.markdown(text))