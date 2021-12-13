from django import http

# https://stackoverflow.com/questions/26359718/django-remove-www-from-urls
class NoWWWRedirectMiddleware(object):
    def process_request(self, request):
        host = request.get_host()
        if host.startswith("www."):
            if request.method == "GET":
                no_www_host = host[4:]
                url = request.build_absolute_uri().replace(host, no_www_host, 1)
                return http.HttpResponsePermanentRedirect(url)
