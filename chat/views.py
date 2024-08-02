from django.http import HttpRequest
from django.http.response import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,redirect
from django.views.generic import CreateView,FormView,TemplateView,ListView,View,DetailView,UpdateView
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse_lazy
from chat.forms import UserForm,LoginForm,PostForm,UserDetailsForm,ChatForm,CommentForm,GroupCreateForm,GroupChatForm
from chat.models import Posts,UserDetails,ChatMessages,Comments,Groups,GroupMessages
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.db.models import Q,Max,Count,Sum
from django.http import JsonResponse


def signin_required(fn):
    def wrapper(request,*args,**kw):
        if not request.user.is_authenticated:
            return redirect('signin')
        else:
            return fn(request,*args,**kw)
    return wrapper

# class SignupView(CreateView):
#     def get(self,request,*args,**kw):
#         form = UserForm()
#         return render(request,"Signup.html",{"form":form})
#     def post(self,request,*args,**kw):
#         form = UserForm(request.POST)
#         if form.is_valid():
#             form.save()
#             UserDetails.objects.create(user=form.save(commit=False),pfp="chat/statics/css/default.png",nickname=request.POST.get('username'),bio="im using ECHOTEXT",status="online")
#             pf = UserDetails.objects.get(user=form.save(commit=False))
#             pf.following.add(pf)
#             return redirect('signin')
#         else:
#             return redirect('signin')

class SigninView(FormView):
    template_name = "Signin.html"
    form_class = LoginForm
    success_url = reverse_lazy("home")
    def post(self,request,*args,**kw):
        form = LoginForm(request.POST)
        if form.is_valid():
            usr = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password')
        user = authenticate(request,username=usr,password=pwd)
        if user:
            login(request,user)
            return redirect('explore')
        else:
            return render(request,"Signin.html",{"form":form})
        
def Signout(request,*args,**kw):
    logout(request)
    return redirect("signin")

@method_decorator(signin_required,name='dispatch')
class ExploreView(View):
    def get(self,request,*args,**kw):
        profile = UserDetails.objects.get(user=request.user)
        qs=Posts.objects.filter(profile__in = profile.following.all()).order_by("-id")
        form=PostForm()
        form2=GroupCreateForm()
        people = UserDetails.objects.exclude(user=request.user).order_by('nickname')
        coms=ChatMessages.objects.filter(writer=profile).values_list('reader',flat=True).distinct()
        oppcoms=ChatMessages.objects.filter(reader=profile).values_list('writer',flat=True).distinct()
        outgos=UserDetails.objects.filter(id__in = coms )
        incoms=UserDetails.objects.filter( Q(id__in = oppcoms) & ~Q( id__in = coms ) )
        lastmsg=ChatMessages.objects.values('writer','reader').annotate(last_msg=Max('id')).order_by('writer')
        lastgcmsg=GroupMessages.objects.values('group','text').annotate(last_msg=Max('id')).order_by('group')
        tab=kw.get('tab')
        groups = Groups.objects.filter(members = profile)
        srch = kw.get('srch')
        if srch:
            people = UserDetails.objects.filter(nickname__contains = srch)
        lst=[]
        for i in lastmsg:
            if i.get('writer') == profile.id or i.get('reader') == profile.id:
                lst.append(ChatMessages.objects.get(id=i.get('last_msg')))
        context = {
            "post":qs,
            "form":form,
            "form2":form2,
            "profile":profile,
            "incoms":incoms,
            "outgos":outgos,
            "people":people,
            "groups":groups,
            "lst":lst,
            "tab":tab,
            "lgc":lastgcmsg
                   }
        return render(request,"Explore.html",context)
    def post(self,request,*args,**kw):
        form = PostForm(request.POST,request.FILES)
        form2 = GroupCreateForm(request.POST,request.FILES)
        if form.is_valid():
            fr = form.save(commit=False)
            fr.profile = (UserDetails.objects.get(user=request.user))
            fr.save()
            return redirect("explore")
        if form2.is_valid():
            player=UserDetails.objects.get(user=request.user)
            gc = form2.save(commit=False)
            gc.creator = player
            form2.save()
            gc.admins.add(player)
            gc.members.add(player)
            GroupMessages.objects.create(text='created the group',writer=player,group=gc,msgtype='created')
            return redirect("group",id=gc.id)

@method_decorator(signin_required,name='dispatch')
class GroupView(View):
    def get(self,request,*args,**kw):
        player = UserDetails.objects.get(user=request.user)
        if Groups.objects.get(id=kw.get('id')).members.filter(user=player.user):
            player = UserDetails.objects.get(user=request.user)
            group = Groups.objects.get(id=kw.get('id'),members=player)
            members = group.members.all()
            messages=GroupMessages.objects.filter(group=group).order_by('id')
            form=GroupChatForm()
            followed = player.following.exclude(user=request.user)
            return render(request,"Group_Chat.html",{'player':player,'group':group,'messages':messages,'form':form,'members':members,'followed':followed})
        else:
            return redirect('explore')
    def post(self,request,*args,**kw):
        gcform = GroupCreateForm(request.POST,request.FILES,instance=Groups.objects.get(id=kw.get('id')))
        player = UserDetails.objects.get(user=request.user)
        group = Groups.objects.get(id=kw.get('id'),members=player)
        if gcform.is_valid() and Groups.objects.get(id=kw.get('id'),admins=player) :
            gcform.save(commit=False)
            if 'name' in gcform.cleaned_data:
                group.name = gcform.cleaned_data['name']
            if 'desc' in gcform.cleaned_data:
                group.desc = gcform.cleaned_data['desc']
            if 'icon' in gcform.cleaned_data:
                group.icon = gcform.cleaned_data['icon']
            group.save()
            return redirect("group",id=kw.get('id'))

def group_add(request,*args,**kw):
    player = UserDetails.objects.get(user=request.user)
    opp = UserDetails.objects.get(id=kw.get('uid'))
    group=Groups.objects.get(id=kw.get('id'),admins =player)
    group.members.add(opp)
    GroupMessages.objects.create(text='joined the Group',writer=opp,group=group,msgtype='added')
    return redirect("group",id=kw.get('id'))

def group_remove(request,*args,**kw):
    player = UserDetails.objects.get(user=request.user)
    opp = UserDetails.objects.get(id=kw.get('uid'))
    group=Groups.objects.get(id=kw.get('id'),admins =player)
    if opp!=group.creator:
        group.members.remove(opp)
        group.admins.remove(opp)
        GroupMessages.objects.create(text='was removed',writer=opp,group=group,msgtype='kicked')
    return redirect("group",id=kw.get('id'))

def group_leave(request,*args,**kw):
    player = UserDetails.objects.get(user=request.user)
    group=Groups.objects.get(id=kw.get('id'))
    if player!=group.creator:
        GroupMessages.objects.create(text='left the group',writer=player,group=group,msgtype='left')
        group.members.remove(player)
        return redirect("explore")
    elif group.members.all().count() == 1:
        group.members.remove(player)
        group.delete()
        return redirect("explore")
    return redirect("group",id=kw.get('id'))

def group_admin(request,*args,**kw):
    player = UserDetails.objects.get(user=request.user)
    opp = UserDetails.objects.get(id=kw.get('uid'))
    group=Groups.objects.get(id=kw.get('id'),admins =player)
    if opp in group.admins.all() and opp!=group.creator:
        group.admins.remove(opp)
    else:
        group.admins.add(opp)
    return redirect("group",id=kw.get('id'))
        
@method_decorator(signin_required,name='dispatch')
class GroupMsgDeleteView(View):
    def get(self,request,*args,**kw):
        GroupMessages.objects.filter(writer=UserDetails.objects.get(user=request.user),id=kw.get('pk')).delete()
        return redirect('group',id=kw.get('id'))

@method_decorator(signin_required,name='dispatch')
class PostDetailsView(DetailView):
    def get(self,request,*args,**kw):
        pf = UserDetails.objects.get(user=request.user)
        qs=Posts.objects.filter(profile__in = pf.following.all()).order_by("-id")
        people = UserDetails.objects.exclude(user=request.user)
        postdetail = Posts.objects.get(id=kw.get('id'))
        comments = Comments.objects.filter(post=kw.get('id'))
        liked = pf in postdetail.likes.all()
        form=PostForm()
        return render(request,"Explore.html",{"post":qs,"form":form,"liked":liked,"comments":comments,"profile":pf,"people":people,"postdetail":postdetail,"pk":kw.get('id')})
    def post(self,request,*args,**kw):
        form = CommentForm(request.POST,request.FILES)
        if form.is_valid():
            fr = form.save(commit=False)
            fr.user = (UserDetails.objects.get(user=request.user))
            fr.post = (Posts.objects.get(id=kw.get('id')))
            form.save()
            return redirect("postdetail",id=kw.get('id'))
        else:
            return redirect("postdetail",id=kw.get('id'))

class PostOpenView(View):
    def get(self,request,*args,**kw):
        if kw.get('type')=='p':
            post = Posts.objects.get(id=kw.get('id'))
        elif kw.get('type')=='g':
            post = GroupMessages.objects.get(id=kw.get('id'))
        elif kw.get('type')=='m':
            post = ChatMessages.objects.get(id=kw.get('id'))
        return render(request,"Postopen.html",{"post":post})

@method_decorator(signin_required,name='dispatch')
class LikeView(View):
    def get(self,request,*args,**kw):
        pf = UserDetails.objects.get(user=request.user)
        post = Posts.objects.get(id=kw.get('id'))
        if pf in post.likes.all():
            post.likes.remove(pf)
        else:
            post.likes.add(pf)
        return redirect("postdetail",id=kw.get('id'))
    
@method_decorator(signin_required,name='dispatch')
class LikeCmtView(View):
    def get(self,request,*args,**kw):
        pf = UserDetails.objects.get(user=request.user)
        cmt = Comments.objects.get(id=kw.get('cmt'))
        if pf in cmt.likes.all():
            cmt.likes.remove(pf)
        else:
            cmt.likes.add(pf)
        return redirect("postdetail",id=kw.get('id'))
    
@method_decorator(signin_required,name='dispatch')
class FollowView(View):
    def get(self,request,*args,**kw):
        pf = UserDetails.objects.get(user=request.user)
        opp = UserDetails.objects.get(id=kw.get('pk'))
        if opp in pf.following.all():
            pf.following.remove(opp)
        else:
            pf.following.add(opp)
        return redirect("userdetail",pk=kw.get('pk'))

@method_decorator(signin_required,name='dispatch')
class UserUpdateView(UpdateView):
    model= UserDetails
    template_name = 'UserDetails.html'
    fields=["pfp","nickname","bio","status"]
    def get_success_url(self):
          return reverse_lazy('userdetail', kwargs={'pk': self.kwargs['pk']})
    def get(self,request,*args,**kw):
        if request.user!=UserDetails.objects.get(id=kw.get('pk')).user:
            return redirect('userdetail',pk=kw.get('pk'))
        form = UserDetailsForm
        qs=Posts.objects.filter(profile=UserDetails.objects.get(id=kw.get('pk')))
        pf = UserDetails.objects.get(id=kw.get('pk'))
        return render(request,"UserDetails.html",{"posted":qs,"form":form,"profile":pf})

@method_decorator(signin_required,name='dispatch')
class UserProfileView(View):
    def get(self,request,*args,**kw):
        qs=Posts.objects.filter(profile=UserDetails.objects.get(id=kw.get('pk')))
        pf = UserDetails.objects.get(id=kw.get('pk'))
        follwed = pf in UserDetails.objects.get(user=request.user).following.all()
        return render(request,"UserDetails.html",{"posted":qs,"profile":pf,"followed":follwed})

@method_decorator(signin_required,name='dispatch')
class UserPostDetailView(View):
    def get(self,request,*args,**kw):
        qs=Posts.objects.filter(profile=UserDetails.objects.get(id=kw.get('pk')))
        postdetail = Posts.objects.get(id=kw.get('dtl'))
        pf = UserDetails.objects.get(id=kw.get('pk'))
        return render(request,"UserDetails.html",{"posted":qs,"profile":pf,"dtl":kw.get('dtl'),"postdetail":postdetail})

@method_decorator(signin_required,name='dispatch')
class PostDeleteView(View):
    def get(self,request,*args,**kw):
        Posts.objects.filter(profile=UserDetails.objects.get(user=request.user),id=kw.get('dtl')).delete()
        return redirect('userdetail',pk=UserDetails.objects.get(user=request.user).id)

@method_decorator(signin_required,name='dispatch')
class ChatView(View):
    def get(self,request,*args,**kw):
        player = UserDetails.objects.get(user=request.user)
        opp = UserDetails.objects.get(id=kw.get('id'))
        messages=ChatMessages.objects.filter( Q(writer=player,reader=opp ) | Q(writer=opp,reader=player)).order_by('id')
        coms=ChatMessages.objects.filter(writer=player).values_list('reader',flat=True).distinct()
        outgos=UserDetails.objects.filter(id__in = coms )
        form=ChatForm()
        return render(request,"chatscreen.html",{"form":form,"messages":messages,"outgos":outgos,"player":player,"opp":opp})
    def post(self,request,*args,**kw):
        form = ChatForm(request.POST,request.FILES)
        if form.is_valid():
            player = UserDetails.objects.get(user=request.user)
            opp = UserDetails.objects.get(id=kw.get('id'))
            fr = form.save(commit=False)
            fr.writer = (player)
            fr.reader = (opp)
            form.save()
            return redirect("chat",id=kw.get('id'))
        else:
            print (form.errors)
            return redirect("chat",id=kw.get('id'))
        
class ChatajView(View):
    def get(self,request,*args,**kw):
        player = UserDetails.objects.get(user=request.user)
        opp = UserDetails.objects.get(id=kw.get('id'))
        msg=list(ChatMessages.objects.filter( Q(writer=player,reader=opp ) | Q(writer=opp,reader=player)).order_by('id').values('writer__nickname','writer__id','text','time','image','id'))
        return JsonResponse({'msg':msg,'userp':int(player.id),'usero':kw.get('id')})
    def post(self,request,*args,**kw):
        form = ChatForm(request.POST,request.FILES)
        if form.is_valid():
            player = UserDetails.objects.get(user=request.user)
            opp = UserDetails.objects.get(id=kw.get('id'))
            fr = form.save(commit=False)
            fr.writer = (player)
            fr.reader = (opp)
            form.save()
        return JsonResponse({})

class GroupajView(View):
    def get(self,request,*args,**kw):
        player = UserDetails.objects.get(user=request.user)
        if Groups.objects.get(id=kw.get('id')).members.filter(user=player.user):
            player = UserDetails.objects.get(user=request.user)
            group = Groups.objects.get(id=kw.get('id'),members=player)
            msg=list(GroupMessages.objects.filter(group=group).order_by('id').values('writer__nickname','writer__id','text','time','msgtype','image','id'))
            return JsonResponse({'msg':msg,'userp':int(player.id),'gc':kw.get('id')})
        else:
            return redirect('explore')
    def post(self,request,*args,**kw):
        form = GroupChatForm(request.POST,request.FILES)
        player = UserDetails.objects.get(user=request.user)
        group = Groups.objects.get(id=kw.get('id'),members=player)
        if form.is_valid():
            fr = form.save(commit=False)
            fr.writer = (player)
            fr.group = (group)
            form.save()
            return redirect("group",id=kw.get('id'))

@method_decorator(signin_required,name='dispatch')
class MessageDeleteView(View):
    def get(self,request,*args,**kw):
        ChatMessages.objects.filter(writer=UserDetails.objects.get(user=request.user),id=kw.get('pk')).delete()
        return redirect('chat',id=kw.get('id'))

class SignupView(CreateView):
    def get(self,request,*args,**kw):
        form = UserForm()
        return render(request,"Signup.html",{"form":form})
    def post(self,request,*args,**kw):
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            UserDetails.objects.create(user=form.save(commit=False),pfp="chat/statics/pfp/default.png",nickname=request.POST.get('username'),bio="im using ECHOTEXT",status="online")
            pf = UserDetails.objects.get(user=form.save(commit=False))
            pf.following.add(pf)
            return redirect('signin')
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{form.fields[field].label}: {error}")
            return render(request,"Signup.html",{"form":form,"errors":errors})
        
class aboutView(TemplateView):
    template_name='About.html'

class MyActivityView(View):
    def get(self,request,*args,**kw):
        player=UserDetails.objects.get(user=request.user)
        c={
            "profile":player,

            "total_likes":Posts.objects.filter(profile=player).aggregate(total_likes=Count('likes'))['total_likes'],
            "likes_given":Posts.objects.filter(likes=player).count(),
            "total_cmt":Comments.objects.filter(post__profile=player).count(),
            "cmt_given":Comments.objects.filter(user=player).count(),
            "cmt_likes":Comments.objects.filter(user=player).aggregate(total_likes=Count('likes'))['total_likes'],

            "msg_sent":ChatMessages.objects.filter(writer=player).count(),
            "msg_sent_users":ChatMessages.objects.filter(writer=player).values('reader').distinct().count(),
            "gm_sent":GroupMessages.objects.filter(writer=player,msgtype='message').count(),
            "gm_sent_gc":GroupMessages.objects.filter(writer=player,msgtype='message').values('group').distinct().count(),
            "msg_rec":ChatMessages.objects.filter(reader=player).count(),
            "msg_rec_users":ChatMessages.objects.filter(reader=player).values('writer').distinct().count(),
            "gm_rec":GroupMessages.objects.filter(group__members=player,msgtype='message').exclude(writer=player).count(),
            "gm_rec_gc":GroupMessages.objects.filter(group__members=player,msgtype='message').exclude(writer=player).values('group').distinct().count(),
            "gc_created":Groups.objects.filter(creator=player).count(),
            "gc_mod":Groups.objects.filter(admins=player).count(),
            "gc_joined":Groups.objects.filter(members=player).count(),
            
        }
        return render(request,"MyActivity.html",c)

class ConnectionsView(View):
    def get(self,request,*args,**kw):
        player=UserDetails.objects.get(user=request.user)
        c={
            "profile":player,
            "followers":UserDetails.objects.filter(following=player).exclude(id=player.id),
            "following":player.following.all().exclude(id=player.id),
        }
        print(c )
        return render(request,"Connections.html",c)
