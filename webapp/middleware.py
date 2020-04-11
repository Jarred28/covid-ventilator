from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework.reverse import reverse

class AuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.path == '/' and not '/accounts/' in request.path and not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login', request=request))
        elif (request.path == '/' or '/accounts/' in request.path) and request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home', request=request))
        return None
