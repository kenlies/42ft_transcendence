from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from .models import Account


##### USER ENDPOINT #####

def user_view(request):
	if (request.method == 'POST'): ##create user
		try:
			data = json.loads(request.body)
			avatar = 'api/static/avatars/default.png'
			toSetUsername = data.get('username')
			toSetEmail = data.get('email')
			toSetPassword = data.get('password')
			newUser = User.objects.create_user(toSetUsername, toSetEmail, toSetPassword)
			newUser.save()
			newAccount = Account(
				user= newUser,
				avatar= avatar,
			)
			newAccount.save()
			return HttpResponse('User created', status=201)
		except Exception as e:
			return HttpResponse(e, status=500)
	if request.user.is_authenticated:
		if (request.method == 'GET'): ##get user data
			try:
				getUsername = request.GET.get('username')
				currentAccount = Account.objects.get(user__username=getUsername)
				try:
					allFriends = currentAccount.friendList.all()
				except:
					allFriends = []
				allFriendsUsernames = []
				for friend in allFriends:
					allFriendsUsernames.append(friend.user.username)
				try:
					allBlocked = currentAccount.blockedList.all()
				except:
					allBlocked = []
				allBlockedUsernames = []
				for block in allBlocked:
					allBlockedUsernames.append(block.user.username)
				userData = {
					'username': currentAccount.user.username,
					'email': currentAccount.user.email,
					'avatar_url': '/api/avatar?username=' + currentAccount.user.username,
					'friends': allFriendsUsernames,
					'blocked': allBlockedUsernames,
				}
				return HttpResponse(json.dumps(userData), status=200)
			except:
				return HttpResponse('User not found', status=404)
		if (request.method == 'DELETE'): ##delete user
			try:
				data = json.loads(request.body)
				deleteUsername = data.get('username')
				user = Account.objects.get(user__username=deleteUsername)
				user.delete()
				return HttpResponse('User deleted', status=200)
			except Exception as e:
				return HttpResponse('User not found', status=404)
		if (request.method == 'PUT'): ##change user password
			try:
				data = json.loads(request.body)
				toChangeUsername = data.get('username')
				account = User.objects.get(username=toChangeUsername)
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