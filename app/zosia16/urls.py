"""zosia16 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, re_path
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path

urlpatterns = \
    [
        # site URLs
        re_path(r'^admin/', admin.site.urls),
        re_path(r'^accounts/', include('users.urls')),
        re_path(r'', include('conferences.urls')),
        re_path(r'^rooms/', include('rooms.urls')),
        re_path(r'^blog/', include('blog.urls')),
        re_path(r'^sponsors/', include('sponsors.urls')),
        re_path(r'^lectures/', include('lectures.urls')),
        re_path(r'^questions/', include('questions.urls')),

        # API URLs
        re_path(r'^api/v1/rooms/', include(('rooms.api.urls', 'rooms'), namespace='v1')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# NOTE: It only serve static files when debug=True

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [re_path(r'^__debug__/', include(debug_toolbar.urls))]
