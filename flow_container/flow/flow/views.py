from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render

@ensure_csrf_cookie
def index(request):
	template = loader.get_template('pong/index.html')
	return HttpResponse(template.render())

@ensure_csrf_cookie
def stylesheet(request):
	return render(request, 'css/styles.css', {}, content_type="text/css")
