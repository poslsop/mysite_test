from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from .models import Blog, BlogType
from django.conf import settings
from read_statistics.utils import read_statistics_once_read

#each_page_blogs_number = 7

# Create your views here.
def get_blog_list_common_date(request, blog_all_list):
    paginator = Paginator(blog_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    page_num = request.GET.get('page', 1)  # 获取第多少页，默认为1
    page_of_blogs = paginator.get_page(page_num)  # 此方法会处理传入的参数，传入超过范围的或者不是数字的都默认为1，此方法返回一个对象
    current_page_num = page_of_blogs.number  # 当前页码
    # page_range = [current_page_num-2, current_page_num-1, current_page_num, current_page_num+1, current_page_num+2]
    # 获取当前页的前两页和后两页
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    #获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    #nnotate的中文意思是注释，一个更好的理解是分组(Group By)。如果你想要对数据集先进行分组然后再进行某些聚合操作或排序时，需要使用annotate方法来实现。
    # context['blogs'] = page_of_blogs.object_list
    # 获取博客分类对应博客数量
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))#blog_count为自己定义的字段名
    context['page_range'] = page_range
    context['blog_dates'] = Blog.objects.dates('created_time', 'month', order="DESC")
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blog_all_list = Blog.objects.all()
    context = get_blog_list_common_date(request, blog_all_list)
    return render(request, 'blog/blog_list.html', context)

def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk = blog_type_pk)
    blog_all_list = Blog.objects.filter(blog_type= blog_type)
    context = get_blog_list_common_date(request, blog_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_type.html', context)

def blogs_with_date(request, year, month):
    blog_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_date(request, blog_all_list)
    context['blog_dates'] = Blog.objects.dates('created_time', 'month', order="DESC")
    return render(request, 'blog/blogs_with_date.html', context)

def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    context = {}
    #获取当前篇的上一篇博客
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    # 获取当前篇的下一篇博客
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render(request,'blog/blog_detail.html', context)
    #max_age指4有效期有多少秒， expires指定某个时间过期，
    #若两个参数同时存在，第二个参数生效，两个参数都不设置，默认为退出浏览器cookies失效
    #response.set_cookie('blog_%s_reader'%blog_pk, 'true',max_age=60, expires=datetime)
    response.set_cookie(read_cookie_key, 'true')#阅读cookie标记
    return response