from django.conf.urls import url

import msadmin.qa.json
from . import qaviews


urlpatterns = [
    url(r'^main/$', qaviews.main, name='qauth_main'),
    url(r'^prob/create/$', qaviews.create_problem, name='qauth_create_prob'),
    url(r'^prob/save/$', qaviews.save_problem, name='qauth_save_prob'),
    url(r'^prob/save/prob/(?P<probId>\d+)/media/$', msadmin.qa.json.save_problem_media, name='qauth_save_problem_media'),
    url(r'^prob/edit/(?P<probId>\d+)/$', qaviews.edit_problem, name='qauth_edit_prob'),
    url(r'^problem/(?P<probId>\d+)/$', msadmin.qa.json.getProblemJSON, name='qauth_get_problem'),
    url(r'^hint/(?P<hintId>\d+)/$', msadmin.qa.json.getHint, name='qauth_get_hint'),
    url(r'^prob/(?P<probId>\d+)/hint/save/$', msadmin.qa.json.saveHint, name='qauth_save_hint'),
    url(r'^prob/(?P<probId>\d+)/hints/save/$', msadmin.qa.json.saveHints, name='qauth_save_hints'),
    url(r'^prob/(?P<probId>\d+)/hint/delete/$', qaviews.deleteHints, name='qauth_delete_hints'),
    url(r'^prob/(?P<probId>\d+)/media/delete/$', msadmin.qa.json.deleteMedia, name='qauth_delete_media'),
    url(r'^prob/(?P<probId>\d+)/metaInfo/$', msadmin.qa.json.save_problem_meta_info, name='qauth_save_problem_meta_info'),
    url(r'^layouts/$', msadmin.qa.json.getLayouts, name='qauth_layouts'),
    url(r'^prob/(?P<probId>-?\d+)/standards/$', msadmin.qa.json.getStandards, name='qauth_standards'),
    url(r'^prob/image/(?P<probId>\d+)/image/$', msadmin.qa.json.removeProblemImage, name='qauth_remove_problem_image'),
    url(r'^prob/image/(?P<probId>\d+)/audio/$', msadmin.qa.json.removeProblemAudio, name='qauth_remove_problem_audio'),
    url(r'^hint/audio/(?P<hintId>\d+)/$', msadmin.qa.json.removeHintAudio, name='qauth_remove_hint_audio'),
    url(r'^hint/image/(?P<hintId>\d+)/$', msadmin.qa.json.removeHintImage, name='qauth_remove_hint_image'),
    url(r'^problems/delete/$', msadmin.qa.json.deleteProblems, name='qauth_delete_problems')
]


