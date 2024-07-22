from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_view),
	path('logout', views.logout_view),
    path('send/message', views.send_messages_view),
	path('receive/messages', views.received_messages_view),
    path('avatar', views.avatar_view),
    path('user', views.user_view),
    path('block', views.block_view),
    path('friend', views.friend_view),
    path('ping', views.ping_view),
]
