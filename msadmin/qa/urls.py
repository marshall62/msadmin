from django.conf.urls import url
from . import qaviews

urlpatterns = [
    url(r'^qauth/$', qaviews.main, name='qauth_main'),
    url(r'^prob/create/$', qaviews.create_problem, name='qauth_create_prob'),
    url(r'^prob/save/$', qaviews.save_problem, name='qauth_save_prob'),
    url(r'^prob/save/prob/(?P<probId>\d+)/media/$', qaviews.save_problem_media, name='qauth_save_problem_media'),
    url(r'^prob/edit/(?P<probId>\d+)/$', qaviews.edit_problem, name='qauth_edit_prob'),
    url(r'^problem/(?P<probId>\d+)/$', qaviews.getProblemJSON, name='qauth_get_problem'),
    url(r'^hint/(?P<hintId>\d+)/$', qaviews.getHint, name='qauth_get_hint'),
    url(r'^prob/(?P<probId>\d+)/hint/save/$', qaviews.saveHint, name='qauth_save_hint'),
    url(r'^prob/(?P<probId>\d+)/hints/save/$', qaviews.saveHints, name='qauth_save_hints'),
    url(r'^prob/(?P<probId>\d+)/hint/delete/$', qaviews.deleteHints, name='qauth_delete_hints'),
    url(r'^prob/(?P<probId>\d+)/media/delete/$', qaviews.deleteMedia, name='qauth_delete_media'),
    url(r'^layouts/$', qaviews.getLayouts, name='qauth_layouts')
]