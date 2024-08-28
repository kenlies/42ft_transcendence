from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from api.models import Account, MatchRecords

@ensure_csrf_cookie
def index(request):
	template = loader.get_template('pong/index.html')
	return HttpResponse(template.render())

@ensure_csrf_cookie
def stylesheet(request):
	return render(request, 'css/styles.css', {}, content_type="text/css")

@ensure_csrf_cookie
def javascript(request):
	return render(request, 'js/scripts.js', {}, content_type="text/javascript")

@ensure_csrf_cookie
def content(request, content, subdir=None, targetUsername=None):
	no_allow = [
		'index',
	]
	no_auth = [
		'login',
		'register',
		'landing',
	]
	if (request.method == 'GET'):
		context = {}
		if (content in no_auth or request.user.is_authenticated) and content not in no_allow:
			try:
				user = Account.objects.get(user=request.user)
				context['user'] = user
				context['blocked'] = user.blockedList.all()
				context['friends'] = user.friendList.all()

				if targetUsername:
					targetUser = Account.objects.get(user__username=targetUsername)
					context['targetUser'] = targetUser
					matches = MatchRecords.objects.filter(account=targetUser)
					context['match'] = {
						"count": matches.count(),
						"wins": matches.filter(result='Win').count(),
						"losses": matches.filter(result='Loss').count()
					}
					context['matchData'] = matches.values('match__matchDate', 'opponent', 'score', 'result')

					if targetUser not in context['blocked']:
						receivedMessages = user.receivedMessages.filter(messageSender=targetUser).order_by('messageDate')
						sentMessages = user.sentMessages.filter(messageReceiver=targetUser).order_by('messageDate')
						context['messages'] = (receivedMessages | sentMessages).order_by('messageDate')
					else:
						context['messages'] = None
				else:
					matches = MatchRecords.objects.filter(account=user)
					context['match'] = {
						"count": matches.count(),
						"wins": matches.filter(result='Win').count(),
						"losses": matches.filter(result='Loss').count()
					}
					context['matchData'] = matches.values('match__matchDate', 'opponent', 'score', 'result')
					context['targetUser'] = user
					context['messages'] = None
			except:
				context['user'] = None
				context['friends'] = None
				context['blocked'] = None
				context['targetUser'] = None
				context['match'] = None
				context['matchData'] = None
				context['messages'] = None
			try:
				if subdir:
					template = loader.get_template('pong/' + subdir + '/' + content + '.html')
				else:
					template = loader.get_template('pong/' + content + '.html')
			except:
				return HttpResponse('Content not found', status=404)
		else:
			return HttpResponse('Unauthorized', status=401)
		return HttpResponse(template.render(context))
	else:
		return HttpResponse('Method not allowed', status=405)

@ensure_csrf_cookie
def joinlobby(request):
	if request.user.is_authenticated:
		if request.method == 'GET':
			try:
				user = Account.objects.get(user=request.user)
				context = {}
				gameUrl = request.GET.get('gameUrl')
				if 'onlineTournament' in gameUrl:
					gameMode = 'onlineTournament'
				elif 'localTournament' in gameUrl:
					gameMode = 'localTournament'
				elif 'online' in gameUrl:
					gameMode = 'online'
				else:
					gameMode = 'local'
				context["response"] = {"url": gameUrl, 'gameMode': gameMode}
				context["username"] = request.user.username
				context['blocked'] = [blocked_user.user.username for blocked_user in user.blockedList.all()]
				return render(request, 'pong/lobby.html', context)
			except:
				return HttpResponse('Invalid lobby', status=400)
		else:
			return HttpResponse('Method not allowed', status=405)
	else:
		return HttpResponse('Unauthorized', status=401)
