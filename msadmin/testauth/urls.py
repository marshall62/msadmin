from django.conf.urls import url
from . import tests, questions

urlpatterns = [
    url(r'^testauth/$', tests.main, name='testauth_main'),
    url(r'^testauth/tests/$', tests.main, name='testauth_tests_main'), # get & post
    url(r'^testauth/tests/new/$', tests.newTest, name='testauth_tests_new'),
    url(r'^testauth/tests/(?P<testId>\d+)/$', tests.getTest, name='testauth_tests_getTest'),
    url(r'^testauth/tests/(?P<testId>\d+)/allQuestions/$', tests.getTestQuestions, name='testauth_tests_getQuestions'),
    url(r'^testauth/tests/(?P<testId>\d+)/questions/$', tests.addQuestions, name='testauth_tests_addQuestions'),
    url(r'^testauth/tests/(?P<testId>\d+)/questions/order/$', tests.orderQuestions, name='testauth_tests_orderQuestions'),
    url(r'^testauth/tests/(?P<testId>\d+)/questions/(?P<qId>\d+)/$', tests.question, name='testauth_tests_question'),
    url(r'^testauth/tests/(?P<testId>\d+)/$', tests.test, name='testauth_tests_test'),
    url(r'^testauth/tests/(?P<testId>\d+)/questions/(?P<qId>\d+)/preview/$', tests.previewQuestion, name='testauth_tests_previewQuestion'),
    url(r'^testauth/questions/$', questions.main, name='testauth_questions_main'), # get,post,delete
    url(r'^testauth/questions/all/$', questions.all, name='testauth_questions_all'),
    url(r'^testauth/questions/new/$', questions.newQuestion, name='testauth_questions_newQuestion'),
    url(r'^testauth/questions/(?P<qId>\d+)/$', questions.question, name='testauth_questions_question'), # get/post
    url(r'^testauth/questions/(?P<qId>\d+)/tests/(?P<testId>\d+)/$', questions.newQuestion, name='testauth_questions_newQuestion'), # get/post
    url(r'^testauth/questions/(?P<qId>\d+)/img/$', questions.getQuestionImage, name='testauth_questions_getQuestionImage'),
    url(r'^testauth/questions/(?P<qId>\d+)/descr/$', questions.getQuestionDescription, name='testauth_questions_getQuestionDescription'),
    url(r'^testauth/questions/(?P<qId>\d+)/preview/$', questions.previewQuestion, name='testauth_questions_previewQuestion'),


]