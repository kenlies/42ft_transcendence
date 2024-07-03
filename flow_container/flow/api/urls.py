from django.urls import path
from . import views

urlpatterns = [
    path('send/message', views.send_messages_view),
	path('receive/messages', views.received_messages_view),
    path('avatar', views.avatar_view),
    path('user', views.user_view),
    path('block', views.block_view),
]