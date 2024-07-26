from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from .models import Account
from .models import Message
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from datetime import timedelta
from django.utils import timezone


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
				data = request.body
				user = Account.objects.get(user__username=request.user.username)
				user.avatar = data.FILES['avatar']
				user.save()
				return HttpResponse('Avatar changed', status=200)
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
			newUser = User.objects.create_user(data.get('username'),
											   data.get('email'),
											   data.get('password'))
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
				userData = {
					'username': currentAccount.user.username,
					'email': currentAccount.user.email,
					'avatar_url': '/api/avatar?username=' + currentAccount.user.username,
					'friends': allFriendsUsernames,
					'blocked': allBlockedUsernames,
					'is_online': currentAccount.is_online
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
		if (request.method == 'PUT'): ##change user password
			try:
				data = json.loads(request.body)
				account = User.objects.get(username=request.user.username)
				if (data.get('password') != None):
					account.user.set_password(data.get('password'))
					account.user.save()
				return HttpResponse('User updated', status=200)
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
