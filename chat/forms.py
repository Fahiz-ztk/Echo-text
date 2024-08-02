from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from chat.models import Posts,UserDetails,ChatMessages,Comments,Groups,GroupMessages
from PIL import Image
import os
from django.conf import settings

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email','username','password1','password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

class PostForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['text','image','title']
        
    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.image and not instance.thumb:
            instance.save()
            img = Image.open(instance.image.path)
            img.thumbnail((200, 200))
            thumb_dir = os.path.join(settings.BASE_DIR, 'chat/statics/thumb')
            if not os.path.exists(thumb_dir):
                os.makedirs(thumb_dir)
            thumb_path = os.path.join(thumb_dir, os.path.basename(instance.image.path))
            img.save(thumb_path)
            instance.thumb = os.path.join('chat/statics/thumb', os.path.basename(instance.image.path))
        if commit:
            instance.save()
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['text']

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ['pfp','nickname','bio','status']

class ChatForm(forms.ModelForm):
    class Meta:
        model = ChatMessages
        fields = ['image','text']

class GroupChatForm(forms.ModelForm):
    class Meta:
        model = GroupMessages
        fields = ['image','text']

class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = ['name','desc','icon']

    def __init__(self, *args, **kwargs):
        super(GroupCreateForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['desc'].required = False
        self.fields['icon'].required = False
