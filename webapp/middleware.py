from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework.reverse import reverse
from covid.settings import ALLOWED_HTTP_METHODS, METHOD_PARAM_KEY, CSRF_HEADER_NAME

class AuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.path == '/' and not '/accounts/' in request.path and not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login', request=request))
        elif (request.path == '/' or '/accounts/' in request.path) and request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home', request=request))
        return None

class MethodOverrideMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method != 'POST':
            return None
        method = self._get_method_override(request)
        if method in ALLOWED_HTTP_METHODS:
            request.method = method
            if method != 'POST':
                setattr(request, method, request.POST.copy())
                request.META.update({
                  CSRF_HEADER_NAME: request.POST.get('csrfmiddlewaretoken', '')
                })

    def _get_method_override(self, request):
        method = request.POST.get(METHOD_PARAM_KEY)
        return method and method.upper()
