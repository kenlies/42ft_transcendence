from django.contrib import admin
from django.urls import path
from django.urls import re_path
from django.urls import include
from . import views

urlpatterns = [
	path('initiate/online', views.initiate_online_match_view),
	path('initiate/onlineTournament', views.initiate_online_tournament_view),
]
