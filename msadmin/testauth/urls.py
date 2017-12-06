from django.conf.urls import url
from . import taviews

urlpatterns = [ url(r'^testauth/$', taviews.main, name='testauth_main')]