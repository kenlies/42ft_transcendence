from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_view),
	path('logout', views.logout_view),
	path('message', views.messages_view),
    path('avatar', views.avatar_view),
    path('user', views.user_view),
    path('block', views.block_view),
    path('friend', views.friend_view),
    path('ping', views.ping_view),
    path('matchmaker', views.matchmaker_view),
    path('match', views.record_match_view),
]
