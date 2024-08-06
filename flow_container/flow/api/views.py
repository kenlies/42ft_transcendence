from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Account, Message, Match
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from datetime import timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .validation import validate
import json
import requests
import os

##### MATCHMAKER ENDPOINTS #####

def matchmaker_view(request):
	if request.user.is_authenticated:
		if (request.method == 'GET'):
			try:
				gameMode = request.GET.get('gameMode')
				matchmakerUrl = "http://matchmaker:8001/match/initiate/" + gameMode
				data = {
					"secret": os.environ.get("MATCHMAKER_SECRET"),
					"username": request.GET.get('username')
				}
				matchmakerResponse = requests.post(matchmakerUrl, data=json.dumps(data))
				if (matchmakerResponse.status_code == 200):
					toSendToRoomId = matchmakerResponse.json()['game_room']
					retData = {
						"url": "ws://" + os.environ.get("HOST_IP") + ':8001/match/connect/' + gameMode + '/' + toSendToRoomId,
						"ready": matchmakerResponse.json()['ready']
					}
					return HttpResponse(json.dumps(retData), status=200)
				else:
					return HttpResponse('Matchmaker is not available', status=503)
			except:
				return HttpResponse('Internal Server Error', status=500)
		else:
			return HttpResponse('Method not allowed', status=405)
	else:
		return HttpResponse('Unauthorized', status=401)

@csrf_exempt
def record_match_view(request):
	if (request.method == 'POST'):
		try:
			data = json.loads(request.body)
			if (data.get('secret') != os.environ.get("MATCHMAKER_SECRET")):
				return HttpResponse('Unauthorized', status=401)
			newMatch = Match(
				matchId = data.get('matchId'),
				matchDate = timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
				matchWinnerUsername = data.get('matchWinner'),
				matchLoserUsername = data.get('matchLoser'),
				matchWinnerScore = data.get('matchWinnerScore'),
				matchLoserScore = data.get('matchLoserScore'),
			)
			newMatch.save()
			matchWinnerRecord = Account.objects.get(user__username=data.get('matchWinner'))
			matchLoserRecord = Account.objects.get(user__username=data.get('matchLoser'))
			matchLoserRecord.matchHistory.add(newMatch)
			matchWinnerRecord.matchHistory.add(newMatch)
			matchLoserRecord.save()
			matchWinnerRecord.save()
			print("Match recorded")
			return HttpResponse('Match recorded', status=201)
		except Exception as e:
			print(e)
			return HttpResponse(e, status=500)
	else:
		return HttpResponse('Method not allowed', status=405)

##### LOGIN AND LOGOUT ENDPOINTS #####

def login_view(request):
	if (request.method == 'POST'):
		try:
			data = json.loads(request.body)
			user = authenticate(request, username=data.get('username'), password=data.get('password'))
			if user is not None:
				login(request, user)
				request.session['username'] = user.username
				request.session.save()
				acc = Account.objects.get(user=user)
				acc.last_activity = timezone.now()
				acc.save()
				return HttpResponse('Login successful', status=200)
			else:
				return HttpResponse('Login failed', status=401)
		except:
			return HttpResponse('Internal Server Error', status=500)
	else:
		return HttpResponse('Method not allowed', status=405)


def logout_view(request):
	try:
		toLogout = Account.objects.get(user__username=request.user.username)
		toLogout.last_activity = timezone.now() - timedelta(minutes=1) # set the time 1 minute behind, effectively making user offline in the next calculation
		toLogout.save()
		logout(request)
		Session.objects.filter(session_key=request.session.session_key).delete()
		return HttpResponse('Logout successful', status=200)
	except Exception as e:
		print(e)
		return HttpResponse('Logout failed', status=500)


##### AVATAR ENDPOINT #####

def avatar_view(request):
	if request.user.is_authenticated:
		if (request.method == 'GET'): ##get avatar
			try:
				user = Account.objects.get(user__username=request.GET.get('username'))
				return HttpResponse(user.avatar, status=200)
			except Exception as e:
				return HttpResponse(e, status=404)
		if (request.method == 'POST'): #change avatar.
			try:
				user = Account.objects.get(user__username=request.user.username)
				avatar_file = request.FILES.get('avatar')
				if avatar_file:
					user.avatar = avatar_file
					user.save()
					return HttpResponse('Avatar changed', status=200)
				else:
					return HttpResponse('No avatar provided', status=400)
			except Exception as e:
				return HttpResponse(e, status=500)
		else:
			return HttpResponse('Method not allowed', status=405)
	else:
		return HttpResponse('Unauthorized', status=401)


##### MESSAGES ENDPOINTS #####

def messages_view(request):
	if request.user.is_authenticated:
		if (request.method == 'POST'):
			try:
				data = json.loads(request.body)
				sender = Account.objects.get(user__username=request.user.username)
				receiver = Account.objects.get(user__username=data.get('receiver'))
				newMessage = Message(
					messageContent = data.get('content'),
					messageSender = sender,
					messageReceiver = receiver,
					messageDate = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
				)
				newMessage.save()
				sender.sentMessages.add(newMessage)
				receiver.receivedMessages.add(newMessage)
				sender.save()
				receiver.save()
				return HttpResponse('Message sent', status=200)
			except Exception as e:
				return HttpResponse(e, status=500)
		if (request.method == 'GET'):
			try:
				user = Account.objects.get(user__username=request.user.username)
				other = request.GET.get('other')
				allSentMessages = user.sentMessages.filter(messageReceiver__user__username=other)
				allReceivedMessages = user.receivedMessages.filter(messageSender__user__username=other)
				parsedMessages = []
				for message in allSentMessages:
					messageData = {
						'sender': message.messageSender.user.username,
						'receiver': message.messageReceiver.user.username,
						'content': message.messageContent,
						'date': message.messageDate
					}
					parsedMessages.append(messageData)
				for message in allReceivedMessages:
					messageData = {
						'sender': message.messageSender.user.username,
						'receiver': message.messageReceiver.user.username,
						'content': message.messageContent,
						'date': message.messageDate
					}
					parsedMessages.append(messageData)
				sortedMessages = sorted(parsedMessages, key=lambda x: x["date"])
				return HttpResponse(json.dumps(sortedMessages), status=200)
			except Exception as e:
				return HttpResponse(e, status=404)
	else:
		return HttpResponse('Unauthorized', status=401)


##### BLOCK ENDPOINT #####

def block_view(request):
	if request.user.is_authenticated:
		if (request.method == 'POST'): ##add user to blocklist
			try:
				data = json.loads(request.body)
				user = Account.objects.get(user__username=request.user.username)
				user.blockedList.add(Account.objects.get(user__username=data.get('blockUsername')))
				user.save()
				return HttpResponse('User blocked', status=200)
			except Exception as e:
				return HttpResponse(e, status=500)
		if (request.method == 'DELETE'): ##remove user from blocklist
			try:
				data = json.loads(request.body)
				user = Account.objects.get(user__username=request.user.username)
				user.blockedList.remove(Account.objects.get(user__username=data.get('unblockUsername')))
				user.save()
				return HttpResponse('User unblocked', status=200)
			except Exception as e:
				return HttpResponse(e, status=500)
		else:
			return HttpResponse('Method not allowed', status=405)
	else:
		return HttpResponse('Unauthorized', status=401)


##### FRIEND ENDPOINT #####

def friend_view(request):
	if request.user.is_authenticated:
		if (request.method == 'POST'): ##add friend
			try:
				data = json.loads(request.body)
				user = Account.objects.get(user__username=request.user.username)
				user.friendList.add(Account.objects.get(user__username=data.get('friendUsername')))
				user.save()
				return HttpResponse('Friend added', status=200)
			except Exception as e:
				return HttpResponse(e, status=500)
		if (request.method == 'DELETE'): ##delete friend from list
			try:
				data = json.loads(request.body)
				user = Account.objects.get(user__username=request.user.username)
				user.friendList.remove(Account.objects.get(user__username=data.get('friendUsername')))
				user.save()
				return HttpResponse('Friend deleted', status=200)
			except Exception as e:
				return HttpResponse(e, status=500)
		else:
			return HttpResponse('Method not allowed', status=405)
	else:
		return HttpResponse('Unauthorized', status=401)


##### USER ENDPOINT #####

def user_view(request):
	if (request.method == 'POST'): ##create user
		try:
			data = json.loads(request.body)
			username = data.get('username')
			email = data.get('email')
			password = data.get('password')
			confirm_password = data.get('confirm_password')
			validation_error = validate({'username': username, 'email': email, 'password': password, 'confirm_password': confirm_password})
			if validation_error:
				return HttpResponse(validation_error, status=400)
			newUser = User.objects.create_user(username, email, password)
			newUser.save()
			newAccount = Account(
				user= newUser,
				avatar= 'api/static/avatars/default.png',
			)
			newAccount.save()
			return HttpResponse('User created', status=201)
		except Exception as e:
			return HttpResponse(e, status=500)
	if request.user.is_authenticated:
		if (request.method == 'GET'): ##get user data
			try:
				currentAccount = Account.objects.get(user__username=request.GET.get('username'))
				allFriendsUsernames = []
				for friend in currentAccount.friendList.all():
					allFriendsUsernames.append(friend.user.username)
				allBlockedUsernames = []
				for block in currentAccount.blockedList.all():
					allBlockedUsernames.append(block.user.username)
				allMatches = currentAccount.matchHistory.all()
				allMatchesData = []
				for match in allMatches:
					matchData = {
						'matchId': match.matchId,
						'matchDate': match.matchDate,
						'matchWinner': match.matchWinnerUsername,
						'matchLoser': match.matchLoserUsername,
						'matchWinnerScore': match.matchWinnerScore,
						'matchLoserScore': match.matchLoserScore,
					}
					allMatchesData.append(matchData)
				userData = {
					'username': currentAccount.user.username,
					'email': currentAccount.user.email,
					'avatar_url': '/api/avatar?username=' + currentAccount.user.username,
					'friends': allFriendsUsernames,
					'blocked': allBlockedUsernames,
					'is_online': currentAccount.is_online,
					'matches': allMatchesData
				}
				return HttpResponse(json.dumps(userData), status=200)
			except:
				return HttpResponse('User not found', status=404)
		if (request.method == 'DELETE'): ##delete user
			try:
				data = json.loads(request.body)
				user = Account.objects.get(user__username=request.user.username)
				user.delete()
				return HttpResponse('User deleted', status=200)
			except Exception as e:
				return HttpResponse('User not found', status=404)
		if (request.method == 'PUT'): ##change user, email, and password
			try:
				data = json.loads(request.body)
				user = Account.objects.get(user__username=request.user.username)
				if 'new_username' in data:
					new_username = data.get('new_username')
					validation_error = validate({'username': new_username})
					if validation_error:
						return HttpResponse(validation_error, status=400)
					user.user.username = new_username
					user.user.save()
				if 'new_email' in data:
					new_email = data.get('new_email')
					validation_error = validate({'email': new_email})
					if validation_error:
						return HttpResponse(validation_error, status=400)
					user.user.email = new_email
					user.user.save()
				if 'password' in data and 'new_password' in data and 'confirm_password' in data:
					current_password = data.get('password')
					new_password = data.get('new_password')
					confirm_password = data.get('confirm_password')
					validation_error = validate({'password': new_password, 'confirm_password': confirm_password})
					if validation_error:
						return HttpResponse(validation_error, status=400)
					if user.user.check_password(current_password):
						user.user.set_password(new_password)
						user.user.save()
					else:
						return HttpResponse('Wrong password', status=401)
				return HttpResponse('Information updated', status=200)
			except Exception as e:
				return HttpResponse(e, status=500)
		else:
			return HttpResponse('Method not allowed', status=405)
	else:
		return HttpResponse('Unauthorized', status=401)

def ping_view(request):
	if request.user.is_authenticated:
		if (request.method == 'POST'):
			try:
				data = json.loads(request.body)
				user = Account.objects.get(user__username=request.user.username)
				user.last_activity = timezone.now()
				user.save()
				return HttpResponse('Updated user last_activity', status=200)
			except Exception as e:
				return HttpResponse(e, status=500)
		else:
			return HttpResponse('Method not allowed', status=405)
	else:
		return HttpResponse('Unauthorized', status=401)
