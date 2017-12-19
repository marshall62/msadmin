from django.db import models

class Question (models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    ansType = models.IntegerField()
    problemSet = models.ForeignKey('ProblemSet',db_column='problemSet')

    aChoice = models.CharField(max_length=200)
    bChoice = models.CharField(max_length=200)
    cChoice = models.CharField(max_length=200)
    dChoice = models.CharField(max_length=200)
    eChoice = models.CharField(max_length=200)
    aURL = models.CharField(max_length=100)
    bURL = models.CharField(max_length=100)
    cURL = models.CharField(max_length=100)
    dURL = models.CharField(max_length=100)
    eURL = models.CharField(max_length=100)
    comment = models.CharField(max_length=100)
    waitTimeSecs = models.IntegerField()
    hoverText = models.CharField(max_length=150)

    MULTI_CHOICE="multichoice"
    SHORT_ANSWER="shortanswer"

    class Meta:
        db_table = "prepostproblem"

class TestQuestionMap (models.Model):
    question = models.ForeignKey('Question',db_column='probId')
    test = models.ForeignKey('Test',db_column='testId')
    position = models.IntegerField()

    class Meta:
        db_table = "prepostproblemtestmap"

class Test (models.Model):
    name = models.CharField(max_length=100)
    isActive = models.BooleanField()
    questions = models.ManyToManyField(Question, through='TestQuestionMap')

    class Meta:
        db_table = "preposttest"