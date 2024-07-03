from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def index(request):
	template = loader.get_template('pong/index.html')
	return HttpResponse(template.render())
