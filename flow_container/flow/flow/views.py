from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from api.models import Account

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
def content(request, content, targetUsername=None):
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
				context['friends'] = user.friendList.exclude(blockedList__in=context['blocked'])

				if targetUsername:
					targetUser = Account.objects.get(user__username=targetUsername)
					context['targetUser'] = targetUser
					matches = targetUser.matchHistory.all()
					context['match'] = {
						"count": matches.count(),
						"wins": matches.filter(matchWinnerUsername=targetUser).count(),
						"losses": matches.filter(matchLoserUsername=targetUser).count()
					}
					context['matchData'] = matches.values('matchDate', 'matchWinnerUsername', 'matchLoserUsername', 'matchWinnerScore', 'matchLoserScore')

					if targetUser not in context['blocked']:
						receivedMessages = user.receivedMessages.filter(messageSender=targetUser).order_by('messageDate')
						sentMessages = user.sentMessages.filter(messageReceiver=targetUser).order_by('messageDate')
						context['messages'] = (receivedMessages | sentMessages).order_by('messageDate')
					else:
						context['messages'] = None
				else:
					matches = user.matchHistory.all()
					context['match'] = {
						"count": matches.count(),
						"wins": matches.filter(matchWinnerUsername=user).count(),
						"losses": matches.filter(matchLoserUsername=user).count()
					}
					context['matchData'] = matches.values('matchDate', 'matchWinnerUsername', 'matchLoserUsername', 'matchWinnerScore', 'matchLoserScore')
					context['targetUser'] = None
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
				template = loader.get_template('pong/' + content + '.html')
			except:
				return HttpResponse('Content not found', status=404)
		else:
			return HttpResponse('Unauthorized', status=401)
		return HttpResponse(template.render(context))
	else:
		return HttpResponse('Method not allowed', status=405)

# in development
import json
from api.views import matchmaker_view
@ensure_csrf_cookie
def startlobby(request):
	response = matchmaker_view(request)
	res = response.content.decode('utf-8')
	context = {}
	context["response"] = json.loads(res)
	context["username"] = request.user.username
	return render(request, 'js/lobby.js', context, content_type="text/javascript")
