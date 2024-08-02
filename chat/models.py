from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os
from django.conf import settings
 
class UserDetails(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    nickname = models.CharField(max_length=50)
    pfp = models.ImageField(upload_to='chat/statics/pfp',null=True)
    bio = models.CharField(max_length=500)
    status = models.CharField(max_length=20)
    following = models.ManyToManyField('self',symmetrical=False)
    def followingcount(self):
        return self.following.all().count()
    def followercount(self):
        return UserDetails.objects.filter(following=self).count()
    def postcount(self):
        return Posts.objects.filter(profile=self).count()
    
    def __str__(self):
        return self.nickname

class Posts(models.Model):
    profile = models.ForeignKey(UserDetails,on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=50,null=True)
    image = models.ImageField(upload_to='chat/statics/posts',null=True)
    thumb = models.ImageField(upload_to='chat/statics/thumb',null=True,blank=True)
    date = models.DateField(auto_now_add=True,null=True)
    text = models.CharField(max_length=600,null=True)
    time = models.TimeField(auto_now_add=True,null=True)
    likes = models.ManyToManyField(UserDetails,related_name='likes')

    def cmtcount(self):
        return Comments.objects.filter(post=self).count()
    def likecount(self):
        return self.likes.all().count()
    def __str__(self):
        return self.title

class ChatMessages(models.Model):
    writer = models.ForeignKey(UserDetails,on_delete=models.CASCADE,related_name='writer')
    reader = models.ForeignKey(UserDetails,on_delete=models.CASCADE,related_name='reader')
    text = models.CharField(max_length=600,null=True)
    image = models.ImageField(upload_to='chat/statics/messages',blank=True,null=True)
    time = models.TimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.text

class Comments(models.Model):
    user = models.ForeignKey(UserDetails,on_delete=models.CASCADE,related_name='cmtuser')
    post = models.ForeignKey(Posts,on_delete=models.CASCADE,related_name='cmtposts')
    text = models.CharField(max_length=500)
    likes = models.ManyToManyField(UserDetails,related_name='cmtlikes')
    datetime =models.DateTimeField(auto_now_add=True)
    
    def likecount(self):
        return self.likes.all().count()
    def __str__(self):
        return self.text
    
class Groups(models.Model):
    creator = models.ForeignKey(UserDetails,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(upload_to='chat/statics/groupicons')
    name= models.CharField(max_length=50)
    desc =models.CharField(max_length=400)
    admins = models.ManyToManyField(UserDetails,related_name='admins')
    members = models.ManyToManyField(UserDetails,related_name='members')

    def __str__(self):
        return self.name
    
    def membercount(self):
        return self.members.all().count()
    
    def gcmembers(self):
        return [i for i in self.members.all()]
    
    def gcadmins(self):
        return [i for i in self.admins.all()]
    
    def last(self):
        return GroupMessages.objects.filter(group=self).order_by('-id').first()
    
class GroupMessages(models.Model):
    writer = models.ForeignKey(UserDetails,on_delete=models.CASCADE,related_name='gwriter')
    group = models.ForeignKey(Groups,on_delete=models.CASCADE)
    text = models.CharField(max_length=600,null=True)
    image = models.ImageField(upload_to='chat/statics/messages',blank=True,null=True)
    time = models.TimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    msgtype = models.CharField(default='message',max_length=10)
    
    def __str__(self):
        return self.text