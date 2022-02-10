from django.http import HttpResponsePermanentRedirect


# https://stackoverflow.com/questions/26359718/django-remove-www-from-urls
class NoWWWRedirectMiddleware:
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        return response or self.get_response(request)

    def process_request(self, request):
        host = request.get_host()
        if host.startswith("www."):
            if request.method == "GET":
                no_www = host[4:]
                url = request.build_absolute_uri().replace(host, no_www, 1)
                return HttpResponsePermanentRedirect(url)
