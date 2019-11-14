from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


# Create your views here.
def post_share(request, post_id):
    post = get_object_or_404(Post,id=post_id, status='published')
    post_url = request.build_absolute_uri(post.get_absolute_url())
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        
        if form.is_valid():
            # get clean data
            cd = form.cleaned_data
            name = cd['name']
            sender = cd['email']
            to = cd['to']
            comments = cd['comments']
            
            # send email
            subject = f'{name} {sender} recommends {post.title}'
            message = f'Read {post.title} at {post_url}\n{name}\'s comments: {comments}'

            send_mail(subject,message,sender,[to])
            sent = True
    else:
        form = EmailPostForm()
    return render(request,'blog/post/share.html',{'post':post,'form':form,'sent':sent, 'post_url':post_url})


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    form = SearchForm()
    query = None

    if 'query' in request.GET:
        form = SearchForm(request.GET)

        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            # search_query = SearchQuery(query)
            object_list = object_list.annotate(
                        # search=search_vector,
                        # rank=SearchRank(search_vector,search_query),
                        similarity=TrigramSimilarity('title',query),
                        ).filter(similarity__gte=0.1).order_by('-similarity')

    if tag_slug:
        tag = get_object_or_404(Tag,slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
        # object_list = object_list.filter(tags__slug=tag_slug)

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    posts = paginator.get_page(page) 

    return render(request, 'blog/post/list.html',{'posts':posts,'tag':tag,'query': query,'form':form})


# class PostListView(ListView):
#     queryset = Post.published.all()
#     paginate_by = 3
#     context_object_name = 'posts'
#     template_name = 'blog/post/list.html'
#     ordering = '-publish'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                    status='published',
                                    publish__year=year,
                                    publish__month=month,
                                    publish__day=day)

    # recommending similar posts by similar tags shared in common
    post_tags_list = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_list).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags',('-publish'))[:4]

    # commenting feature
    comments = post.comments.all()

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # create a comment object but dont commit or save into database 
            new_comment = comment_form.save(commit=False)
            # then assign the post the comment is about
            new_comment.post = post
            # save into database now
            new_comment.save()
    else:
        comment_form = CommentForm()


    return render(request,'blog/post/detail.html',{'post':post,
                                                    'comment_form': comment_form,
                                                    'new_comment':new_comment,
                                                    'comments':comments,'similar_posts': similar_posts})
