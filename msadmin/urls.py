from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.strategy_list, name='strategy_list'),
    url(r'^sc/(?P<pk>\d+)/$', views.sc_detail, name='sc_detail'),
]