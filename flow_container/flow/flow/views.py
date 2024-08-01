from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from api.models import Account

@ensure_csrf_cookie
def index(request):
	template = loader.get_template('pong/index.html')
	context = {}
	if request.user.is_authenticated:
		try:
			context = {
				"user": Account.objects.get(user=request.user)
			}
		except:
			context = {
				"user": None
			}
	return HttpResponse(template.render(context))

@ensure_csrf_cookie
def stylesheet(request):
	return render(request, 'css/styles.css', {}, content_type="text/css")

@ensure_csrf_cookie
def javascript(request):
	return render(request, 'js/scripts.js', {}, content_type="text/javascript")

@ensure_csrf_cookie
def content(request, content):
	if (request.method == 'GET'):
		if content == 'login' or content == 'register' or request.user.is_authenticated:
			try:
				template = loader.get_template('pong/' + content + '.html')
			except:
				return HttpResponse('Content not found', status=404)
		else:
			return HttpResponse('Unauthorized', status=401)
		return HttpResponse(template.render())
	else:
		return HttpResponse('Method not allowed', status=405)
