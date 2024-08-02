"""
URL configuration for texter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chat import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('home/explore',views.ExploreView.as_view(),name='explore'),
    path('home/explore/<str:tab>/',views.ExploreView.as_view(),name='explore_tab'),
    path('home/explore/<str:tab>/<str:srch>',views.ExploreView.as_view(),name='explore_search'),
    path('home/post/<int:id>/',views.PostDetailsView.as_view(),name='postdetail'),
    path('home/post/<int:id>/like',views.LikeView.as_view(),name='like'),
    path('home/post/<int:id>/likecmt/<int:cmt>',views.LikeCmtView.as_view(),name='likecmt'),

    path('home/user/profile/<int:pk>',views.UserProfileView.as_view(),name='userdetail'),
    path('home/user/update/<int:pk>',views.UserUpdateView.as_view(),name='userupdate'),
    path('home/user/follow/<int:pk>',views.FollowView.as_view(),name='follow'),

    path('home/user/profile/<int:pk>/delete/<int:dtl>',views.PostDeleteView.as_view(),name='postdelete'),
    path('home/user/profile/<int:pk>/view/<int:dtl>',views.UserPostDetailView.as_view(),name='userpostdetail'),

    path('home/chat/<int:id>',views.ChatView.as_view(),name='chat'),
    path('home/chat/<int:id>/delete/<int:pk>',views.MessageDeleteView.as_view(),name='msgdelete'),

    path('home/ajchat/<int:id>',views.ChatajView.as_view(),name='ajchat'),
    path('home/ajgroup/<int:id>',views.GroupajView.as_view(),name='ajgroup'),

    path('home/group/<int:id>/',views.GroupView.as_view(),name='group'),
    path('home/group/<int:id>/delete/<int:pk>',views.GroupMsgDeleteView.as_view(),name='gcmsgdelete'),
    path('home/group/<int:id>/add/<int:uid>',views.group_add,name='group_add'),
    path('home/group/<int:id>/remove/<int:uid>',views.group_remove,name='group_remove'),
    path('home/group/<int:id>/leave',views.group_leave,name='group_leave'),
    path('home/group/<int:id>/admin/<int:uid>',views.group_admin,name='group_admin'),

    path('users/signup',views.SignupView.as_view(),name='signup'),
    path('',views.SigninView.as_view(),name='signin'),
    path('users/signout',views.Signout,name='logout'),

    path('home/open/<str:type>/<int:id>/',views.PostOpenView.as_view(),name='postopen'),
    
    path('about',views.aboutView.as_view(),name='about'),
    path('myactivity',views.MyActivityView.as_view(),name='myactivity'),
    path('connections',views.ConnectionsView.as_view(),name='connections'),
]
 