import threading

from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType#ContentType是一张记录app名称与所对应模型的表
from django.contrib.auth.models import User
from django.shortcuts import render

#利用多线程去发送邮件
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
            html_message=self.text
        )


class Comment(models.Model):
    #被评论的对象

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    #评论内容
    text = models.TextField()
    #评论时间
    comment_time = models.DateTimeField(auto_now_add=True)
    # 评论者
    user = models.ForeignKey(User, related_name='comments', on_delete = models.CASCADE)
    """
    related_name是为了防止通过外键反向解析Comment时引起冲突，因为下面的reply_to字段和user字段一样,
    例如：
    若没有related_name, 通过user反向解析Comment：
    from django.contrib.auth.models import User
    user = User.objects.first()
    user.comment_set.all()    模型名小写加下划线set
    
    若有related_name, 通过user反向解析Comment：
    from django.contrib.auth.models import User
    user = User.objects.first()
    user.comments.all()
    user.replies.all()
    
    """
    #记录某一条评论是从哪条评论开始的
    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)

    #指向自己的外键，允许为空
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)
    #被评论者
    reply_to = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.CASCADE)

    def send_mail(self):
        #发送邮件通知
        if self.parent is None:
            #评论我的博客
            subject = '有人评论你的博客'
            email = self.content_object.get_email()
        else:
            #回复评论
            subject = '有人回复你的评论'
            email = self.reply_to.email
        if email != '':
            context = {}
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render(None, 'comment/send_mail.html', context).content.decode('utf-8')
            send_mail = SendMail(subject, text, email)
            send_mail.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-comment_time']


