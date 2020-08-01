from django.shortcuts import render
from django.db.models import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .models import LikeCount, LikeRecord
# Create your views here.

def SuccessResponse(liked_num):
    data = {}
    data['status'] = "SUCCESS"
    data['liked_num'] = liked_num
    return JsonResponse(data)

def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)


def like_change(request):
    #读取数据
    user = request.user
    #验证用户是否登录
    if not user.is_authenticated:
        return ErrorResponse(400, '您尚未登录')
    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))

    try:
        #验证所要点赞的对象是否存在
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return ErrorResponse(401, 'object not exist')

    is_like = request.GET.get('is_like')
    #处理数据
    if is_like == 'true':
        #还未点赞,将要点赞
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
        if created:
            #刚建立，未点赞，进行点赞
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type,object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            #ajax提交数据， 需要返回json格式数据回去
            return SuccessResponse(like_count.liked_num)
        else:
            #已点赞过，不能重复点赞
            return ErrorResponse(402, '你已经点赞过')
    else:
        #已点赞，将要取消点赞
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            #有点赞，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            #点赞总数减1
            #判断LikeCount对象是否建立， 已建立， 则减1
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                #未建立，减1数据错误
                return ErrorResponse(404, '数据错误')
        else:
            #没有点赞过， 不能取消
            return ErrorResponse(403, '没有点过赞，不能取消')


