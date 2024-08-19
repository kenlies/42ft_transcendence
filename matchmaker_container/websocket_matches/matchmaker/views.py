from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import OnlineMatch, OnlineTournament, LocalMatch, LocalTournament
from datetime import datetime
import random
import os
import json

# Create your views here.

def generateId():
	print("Generating ID")
	time = datetime.now().timestamp()
	ret = str(time).replace(".", "-") + '-' + str(random.randint(0, 1000)) + str(random.randint(0, 1000))
	return ret

@csrf_exempt
def initiate_online_match_view(request):
	try:
		if (request.method == 'POST'):
			data = json.loads(request.body)
			if (data["secret"] == os.environ.get("MATCHMAKER_SECRET")):
				# check if there is a match to connect to
				toConnectTo = OnlineMatch.objects.filter(ready=False)
				if (len(toConnectTo) > 0):
					match = toConnectTo[0]
					match.player2 = data["username"]
					match.ready = True
					match.save()
					return HttpResponse(json.dumps({"status": "success", "game_room": match.roomId, "ready": True}), status=200)
				else:
					generatedId = generateId()
					newMatch = OnlineMatch(player1=data["username"], player2="")
					newMatch.roomId = generatedId
					newMatch.save()
					return HttpResponse(json.dumps({"status": "success", "game_room": newMatch.roomId, "ready": False}), status=200)
			else:
				return HttpResponse("Unauthorized", status=401)
		else:
			return HttpResponse('Method not allowed', status=405)
	except Exception as e:
		print(e)
		return HttpResponse("error: " + str(e), status=500)
	
@csrf_exempt
def initiate_online_tournament_view(request):
	try:
		if (request.method == 'POST'):
			data = json.loads(request.body)
			if (data["secret"] == os.environ.get("MATCHMAKER_SECRET")):
				# check if there is a match to connect to
				toConnectTo = OnlineTournament.objects.filter(ready=False)
				if (len(toConnectTo) > 0):
					tournament = toConnectTo[0]
					if (tournament.playerCount == 2):
						tournament.player2 = data["username"]
						tournament.save()
						return HttpResponse(json.dumps({"status": "success", "game_room": tournament.roomId, "ready": False}), status=200)
					elif (tournament.playerCount == 3):
						tournament.player3 = data["username"]
						tournament.save()
						return HttpResponse(json.dumps({"status": "success", "game_room": tournament.roomId, "ready": False}), status=200)
					elif (tournament.playerCount == 4):
						tournament.player4 = data["username"]
						tournament.ready = True
						tournament.save()
						return HttpResponse(json.dumps({"status": "success", "game_room": tournament.roomId, "ready": True}), status=200)
					else:
						return HttpResponse("Not able to connect", status=400)
				else:
					generatedId = generateId()
					newTournament = OnlineTournament(player1=data["username"], player2="", player3="", player4="")
					newTournament.roomId = generatedId
					newTournament.save()
					return HttpResponse(json.dumps({"status": "success", "game_room": newTournament.roomId, "ready": False}), status=200)
			else:
				return HttpResponse("Unauthorized", status=401)
		else:
			return HttpResponse('Method not allowed', status=405)
	except Exception as e:
		print(e)
		return HttpResponse("error: " + str(e), status=500)

@csrf_exempt
def initiate_local_match_view(request):
	try:
		if (request.method == 'POST'):
			data = json.loads(request.body)
			if (data["secret"] == os.environ.get("MATCHMAKER_SECRET")):
				generatedId = generateId()
				newMatch = LocalMatch(player1=data["player1"], player2=data["player2"], roomId=generatedId)
				newMatch.save()
				return HttpResponse(json.dumps({"status": "success", "game_room": newMatch.roomId, "ready": True}), status=200)
			else:
				return HttpResponse("Unauthorized", status=401)
		else:
			return HttpResponse('Method not allowed', status=405)
	except Exception as e:
		print(e)
		return HttpResponse("error: " + str(e), status=500)

@csrf_exempt
def initiate_local_tournament_view(request):
	try:
		if (request.method == 'POST'):
			data = json.loads(request.body)
			if (data["secret"] == os.environ.get("MATCHMAKER_SECRET")):
				generatedId = generateId()
				newTournament = LocalTournament(player1=data["player1"], player2=data["player2"], player3=data["player3"], player4=data["player4"], roomId=generatedId)
				newTournament.save()
				return HttpResponse(json.dumps({"status": "success", "game_room": newTournament.roomId, "ready": True}), status=200)
			else:
				return HttpResponse("Unauthorized", status=401)
		else:
			return HttpResponse('Method not allowed', status=405)
	except Exception as e:
		print(e)
		return HttpResponse("error: " + str(e), status=500)
