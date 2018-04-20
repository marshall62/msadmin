from django.conf.urls import url

import msadmin.topics.topic_views as tv



urlpatterns = [
    url(r'^main/$', tv.main, name='topics_main'),
    url(r'^topic/create/$', tv.create_topic, name='topics_create'),
    url(r'^topic/save/$', tv.save_topic, name='topics_save'),
    url(r'^topic/edit/(?P<topicId>\d+)/$', tv.edit_topic, name='topics_edit'),
    # url(r'^topic/(?P<topicId>\d+)$', tv.qa.json.getProblemJSON, name='topics_get'),

]

