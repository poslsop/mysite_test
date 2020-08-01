from django.db import models
from django.contrib.auth.models import User#引入django自带的用户模型

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)#使用一对一是为了保证一个name只有一个昵称
    #定义昵称
    nickname = models.CharField(max_length=20)

    def __str__(self):
        return '<Profile： %s for %s>'%(self.nickname, self.user.username)

#判断是否有别名，有就返回别名，没有返回‘’
def get_nickname(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return ''
def get_nickname_or_username(self):
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username

def has_nickname(self):
    return Profile.objects.filter(user=self).exists()
User.get_nickname = get_nickname#动态绑定，手动给User添加一个方法
User.get_nickname_or_username = get_nickname_or_username
User.has_nickname = has_nickname