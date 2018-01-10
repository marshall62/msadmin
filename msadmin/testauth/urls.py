from django.conf.urls import url
from . import tests, questions

urlpatterns = [
    # URLs that operate on tests and return HTML page views of the test.
    url(r'^$', tests.main, name='testauth_main'),
    url(r'^pages/tests/$', tests.all_page, name='ta_tests_all_page'), # get all or post ( a new test)
    url(r'^pages/tests/new/$', tests.newTest_page, name='ta_tests_new_page'), # get the page for entering a new test
    url(r'^pages/tests/(?P<testId>\d+)/$', tests.gpTest_page, name='ta_tests_gp_page'), # get / post
    url(r'^pages/tests/(?P<testId>\d+)/questions/new/$', tests.newTestQuestion_page, name='ta_tests_question_new_page'), # get
    url(r'^pages/tests/(?P<testId>\d+)/preview/$', tests.testPreview_page, name='ta_tests_preview_page'), # get
    url(r'^pages/tests/remove/$', tests.deleteTests_page, name='ta_tests_remove_page'), # del tests

    # URLs that operate on questions and return HTML page views of the question
    url(r'^pages/questions/$', questions.all_page, name='ta_questions_all_page'), # get all or post ( a new question) or delete several
    url(r'^pages/questions/new/$', questions.newQuestion_page, name='ta_questions_new_page'), # get the form for entering a new quest
    url(r'^pages/questions/remove/$', questions.deleteQuestions_page, name='ta_questions_remove_page'), # del questions
    url(r'^pages/questions/(?P<qId>\d+)/$', questions.gpQuestion_page, name='ta_questions_gp_page'), # get/post
    url(r'^pages/questions/(?P<qId>\d+)/image/$', questions.getQuestionImage, name='ta_questions_questionImage'), # get image as binary data
    url(r'^pages/questions/(?P<qId>\d+)/preview/$', questions.questionPreview_page, name='ta_questions_preview_page'), # get
    url(r'^pages/tests/(?P<testId>\d+)/questions/(?P<qId>\d+)/preview/$', questions.questionPreview_page, name='ta_tests_question_preview_page'), # GET page preview a tests question


    # URLS that operate on tests and return json
    url(r'^tests/(?P<testId>\d+)/questions/$', tests.testQuestions_json, name='ta_tests_questions_json'),
    url(r'^tests/(?P<testId>\d+)/questions/order/$', tests.testQuestionsOrder_json, name='ta_tests_questions_order_json'),
    url(r'^tests/(?P<testId>\d+)/questions/(?P<qId>\d+)/$', tests.deleteTestQuestions_json, name='ta_tests_questions_del_json'),
    url(r'^tests/(?P<testId>\d+)/questions/add/$', tests.addTestQuestions_json, name='ta_tests_questions_add'),

    # URLs that operate on questions and return JSON
    url(r'^questions/$', questions.all_json, name='ta_questions_all_json'), # get

    url(r'^tests/(?P<testId>\d+)/questions/$', tests.addQuestions, name='testauth_tests_addQuestions'),

    url(r'^tests/(?P<testId>\d+)/questions/order/$', tests.orderQuestions, name='testauth_tests_orderQuestions'),
    url(r'^tests/(?P<testId>\d+)/questions/(?P<qId>\d+)/$', tests.question, name='testauth_tests_question'), # get/ delete
    url(r'^tests/(?P<testId>\d+)/$', tests.test, name='testauth_tests_test'),
    url(r'^tests/(?P<testId>\d+)/preview/$', tests.previewTest, name='testauth_tests_previewTest'),
    url(r'^tests/(?P<testId>\d+)/questions/(?P<qId>\d+)/preview/$', tests.previewQuestion, name='testauth_tests_previewQuestion'),


    url(r'^questions/(?P<qId>\d+)/tests/(?P<testId>\d+)/$', questions.newQuestion, name='testauth_questions_newQuestion'), # get/post
    url(r'^questions/(?P<qId>\d+)/img/$', questions.getQuestionImage, name='testauth_questions_getQuestionImage'),
    url(r'^questions/(?P<qId>\d+)/descr/$', questions.getQuestionDescription, name='testauth_questions_getQuestionDescription'),
    url(r'^questions/(?P<qId>\d+)/preview/$', questions.previewQuestion, name='testauth_questions_previewQuestion'),


]