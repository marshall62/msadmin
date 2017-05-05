from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.strategy_list, name='strategy_list'),
    url(r'^classes/$', views.class_list, name='class_list'),
    url(r'^sc/(?P<pk>\d+)/$', views.sc_detail, name='sc_detail'),
    url(r'^class/(?P<pk>\d+)/$', views.class_detail, name='class_detail'),
    url(r'^strategy/(?P<pk>\d+)/$', views.strategy_detail, name='strategy_detail'),

]