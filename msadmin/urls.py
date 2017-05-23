from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.strategy_list, name='strategy_list'),
    url(r'^classes/$', views.class_list, name='class_list'),
    url(r'^test/$', views.test, name='test'),
    url(r'^sc/(?P<pk>\d+)/$', views.sc_detail, name='sc_detail'),
    url(r'^class/(?P<pk>\d+)/$', views.class_detail, name='class_detail'),
    url(r'^strategy/(?P<pk>\d+)/$', views.strategy_detail, name='strategy_detail'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/$', views.configure_class_strategy, name='class-strategy'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/add$', views.add_class_strategy, name='add-class-strategy'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/remove$', views.remove_class_strategy, name='remove-class-strategy'),
    url(r'^class/(?P<classId>\d+)/sc/(?P<scId>\d+)/is/(?P<isId>\d+)/activate/(?P<isActive>\w+)$', views.class_activate_is, name='intervention-selector-activate'),

]