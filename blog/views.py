from typing import List
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Category

class PostList(ListView):
    model = Post
    ordering='-pk'

    def get_context_data(self,**kwargs):
        context = super(PostList,self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category = None).count()
        return context

class PostDetail(DetailView):
    model = Post

'''
# Create your views here.
 CBV에서 사용하지 않는 함수들 주석 처리
def index(request):
    posts = Post.objects.all().order_by('-pk')

    return render(
        request,
        'blog/index.html',
        {
            'posts': posts,
        }
    )

def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request,
        'blog/single_post_page.html',
        {
            'post': post,
        }
    )
    '''