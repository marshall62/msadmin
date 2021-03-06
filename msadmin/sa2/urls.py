from django.conf.urls import url

from msadmin.qa.qaviews import reactTest
from msadmin.sa2 import views, modelUpdate, json

urlpatterns = [
    url(r'^$', views.main, name='strat_main'),
    url(r'^reactTest/$', reactTest, name='reactTest'),
    url(r'^validate_generic_structure/$', views.validate_generic, name='validate_generic'),
    url(r'^validate_class_tutoring/$', views.validate_class_tutoring, name='validate_class_tutoring'),
    url(r'^classes/(?P<teacherId>.+)/$', views.class_list_by_teacher, name='class_list_by_teacher'),
    url(r'^strategy/generic/$', views.generic_list, name='generic_list'),
    url(r'^classes/$', views.class_list, name='class_list'),
    url(r'^test/$', views.test, name='test'),
    url(r'^sc/(?P<pk>\d+)/$', views.sc_detail, name='sc_detail'),
    url(r'^class/(?P<pk>\d+)/$', views.class_detail, name='class_detail'),
    url(r'^class/(?P<classId>\d+)/save/$', json.class_save, name='class_save'),
    url(r'^strategy/(?P<pk>\d+)/$', views.strategy_detail, name='strategy_detail'),
    url(r'^strategy/(?P<id>\d+)/save/$', modelUpdate.save_strategy, name='strategy_save'),
    url(r'^strategy/(?P<id>\d+)/save/json/$', json.save_generic_strategy, name='generic_strategy_save'),
    url(r'^strategy/(?P<id>\d+)/lc/$', json.get_strategy_lcs, name='strategy_lcs'),
    url(r'^strategy/(?P<strategyId>\d+)/globalize/$', modelUpdate.globalize_strategy, name='globalize-strategy'),
    url(r'^strategy/(?P<strategyId>\d+)/generic/delete/$', views.delete_generic_strategy, name='delete_generic_strategy'),
    url(r'^mathspring/strategy_cache/flush/$', json.flush_strategy_cache, name='flush_strategy_cache'),
    url(r'^mathspring/strategy_cache/flush/strategy/(?P<strategyId>\d+)/$', json.flush_single_strategy_from_cache, name='flush_single_strategy_from_cache'),
    url(r'^all_lcs/$', json.get_all_lcs, name='all_lcs'),
    url(r'^teacher/(?P<teacherId>\d+)/classes/$', json.get_teacher_classes, name='get-teacher-classes'),
    url(r'^class/(?P<classId>\d+)/strategies/$', json.get_class_strategies, name='get-class-strategies'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/$', views.configure_class_strategy, name='class-strategy'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/add$', views.add_class_strategy, name='add-class-strategy'),
    url(r'^class/(?P<classId>\d+)/customStrategy/add$', views.add_class_custom_strategy, name='add-class-custom-strategy'),
    url(r'^class/(?P<classId>\d+)/otherClass/(?P<otherClassId>\d+)/strategy/(?P<stratId>\d+)$', views.add_class_other_class_strategy, name='add-other-class-strategy'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/remove$', views.remove_class_strategy, name='remove-class-strategy'),
    url(r'^class/(?P<classId>\d+)/sc/(?P<scId>\d+)/is/(?P<isId>\d+)/activate/(?P<isActive>\w+)$', views.class_activate_is, name='intervention-selector-activate'),
    url(r'^class/(?P<classId>\d+)/strategy/(?P<strategyId>\d+)/json/$', json.get_strategy_json, name='strategy-json'),
    url(r'^strategy/(?P<strategyId>\d+)/json/$', json.get_generic_strategy_json, name='generic_strategy_json'),
    url(r'^strategyComponent/(?P<scId>\d+)/json/$', json.get_sc_json, name='sc_detail_json'),
    url(r'^class_is_param/(?P<isParamId>\d+)/json/$', json.get_is_param_json, name='class_is_param_detail'),
    url(r'^class_sc_param/(?P<scParamId>\d+)/json/$', json.get_sc_param_json, name='class_sc_param_detail'),
    url(r'^class_is_param/(?P<isParamId>\d+)/save/$', modelUpdate.save_is_param, name='class_is_param_save'),
    url(r'^class_sc_param/(?P<scParamId>\d+)/save/$', modelUpdate.save_sc_param, name='class_sc_param_save'),
    url(r'^class_is/(?P<isId>\d+)/(?P<strategyId>\d+)/save/$', modelUpdate.save_is, name='class_is_save'),
    url(r'^strategyComponent/(?P<scId>\d+)/save/$', modelUpdate.save_sc, name='sc_save'),
    url(r'^class_is_param/(?P<isParamId>\d+)/active/save/$', modelUpdate.save_is_param_active, name='class_is_param_active_save'),
    url(r'^class_sc_param/(?P<scParamId>\d+)/active/save/$', modelUpdate.save_sc_param_active, name='class_sc_param_active_save'),
    url(r'^class_intervSel/(?P<isId>\d+)/active/save/$', modelUpdate.save_intervSel_active, name='class_intervSel_active_save'),
    url(r'^class/(?P<classId>\d+)/is/(?P<isId>\d+)/sc/(?P<scId>\d+)/strategy/(?P<strategyId>\d+)/json/$', json.get_is, name='class_is_detail')

]



# Old QA urls
# url(r'^qauth/$', qaviews.main, name='qauth_main'),
# url(r'^qauth/prob/create/$', qaviews.create_problem, name='qauth_create_prob'),
# url(r'^qauth/prob/save/$', qaviews.save_problem, name='qauth_save_prob'),
# url(r'^qauth/prob/save/prob/(?P<probId>\d+)/media/$', qaviews.save_problem_media, name='qauth_save_problem_media'),
# url(r'^qauth/prob/edit/(?P<probId>\d+)/$', qaviews.edit_problem, name='qauth_edit_prob'),
# url(r'^qauth/problem/(?P<probId>\d+)/$', qaviews.getProblemJSON, name='qauth_get_problem'),
# url(r'^qauth/hint/(?P<hintId>\d+)/$', qaviews.getHint, name='qauth_get_hint'),
# url(r'^qauth/prob/(?P<probId>\d+)/hint/save/$', qaviews.saveHint, name='qauth_save_hint'),
# url(r'^qauth/prob/(?P<probId>\d+)/hints/save/$', qaviews.saveHints, name='qauth_save_hints'),
# url(r'^qauth/prob/(?P<probId>\d+)/hint/delete/$', qaviews.deleteHints, name='qauth_delete_hints'),
# url(r'^qauth/prob/(?P<probId>\d+)/media/delete/$', qaviews.deleteMedia, name='qauth_delete_media'),
# url(r'^qauth/layouts/$', qaviews.getLayouts, name='qauth_layouts')