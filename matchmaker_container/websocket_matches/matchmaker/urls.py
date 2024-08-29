from django.contrib import admin
from django.urls import path
from django.urls import re_path
from django.urls import include
from . import views

urlpatterns = [
	path('initiate/online', views.initiate_online_match_view),
	path('initiate/onlineTournament', views.initiate_online_tournament_view),
	path('initiate/local', views.initiate_local_match_view),
	path('initiate/localTournament', views.initiate_local_tournament_view),
	path('initiate/ai', views.initiate_ai_match_view),
]
