"""msadminsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
import msadmin.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', msadmin.views.main, name='msadmin_main'),
    url(r'^signup/$', msadmin.views.signup, name='msadmin_signup'),
    url(r'^login/$', msadmin.views.login, name='msadmin_login'),
    url(r'^stratauth/', include('msadmin.stratauth.urls')),
    url(r'^qauth/',include('msadmin.qa.urls')),
    url(r'^testauth/',include('msadmin.testauth.urls')),
]
# This adds the ability to get to static media (e.g. uploaded files) using URLS like
# <img src="{{ MEDIA_URL }}{{ problem.getProblemDir }}{{ problem.getImageURL }}"
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)