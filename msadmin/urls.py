from django.conf.urls import url

from . import views

from . import json
from . import modelUpdate


urlpatterns = [
    url(r'^$', views.strategy_list, name='strategy_list'),
    url(r'^classes/(?P<teacherId>.+)/$', views.class_list_by_teacher, name='class_list_by_teacher'),
    url(r'^classes/$', views.class_list, name='class_list'),
    url(r'^test/$', views.test, name='test'),
    url(r'^sc/(?P<pk>\d+)/$', views.sc_detail, name='sc_detail'),
    url(r'^class/(?P<pk>\d+)/$', views.class_detail, name='class_detail'),
    url(r'^strategy/(?P<pk>\d+)/$', views.strategy_detail, name='strategy_detail'),
    url(r'^strategy/(?P<id>\d+)/save/$', modelUpdate.save_strategy, name='strategy_save'),
    url(r'^strategy/(?P<id>\d+)/lc/$', json.get_strategy_lcs, name='strategy_lcs'),
    url(r'^all_lcs/$', json.get_all_lcs, name='all_lcs'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/$', views.configure_class_strategy, name='class-strategy'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/add$', views.add_class_strategy, name='add-class-strategy'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/remove$', views.remove_class_strategy, name='remove-class-strategy'),
    url(r'^class/(?P<classId>\d+)/sc/(?P<scId>\d+)/is/(?P<isId>\d+)/activate/(?P<isActive>\w+)$', views.class_activate_is, name='intervention-selector-activate'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/json/$',json.get_strategy_json, name='strategy-json'),
    url(r'^class_is_param/(?P<isParamId>\d+)/json/$',json.get_is_param_json, name='class_is_param_detail'),
    url(r'^class_sc_param/(?P<scParamId>\d+)/json/$',json.get_sc_param_json, name='class_sc_param_detail'),
    url(r'^class_is_param/(?P<isParamId>\d+)/save/$',modelUpdate.save_is_param, name='class_is_param_save'),
    url(r'^class_sc_param/(?P<scParamId>\d+)/save/$',modelUpdate.save_sc_param, name='class_sc_param_save'),
    url(r'^class_is/(?P<isId>\d+)/save/$',modelUpdate.save_is, name='class_is_save'),
    url(r'^class_is_param/(?P<isParamId>\d+)/active/save/$',modelUpdate.save_is_param_active, name='class_is_param_active_save'),
    url(r'^class_sc_param/(?P<scParamId>\d+)/active/save/$',modelUpdate.save_sc_param_active, name='class_sc_param_active_save'),
    url(r'^class_intervSel/(?P<isId>\d+)/active/save/$',modelUpdate.save_intervSel_active, name='class_intervSel_active_save'),
    url(r'^class/(?P<classId>\d+)/is/(?P<isId>\d+)/sc/(?P<scId>\d+)/json/$',json.get_is, name='class_is_detail')

]