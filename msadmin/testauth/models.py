from django.db import models

class Question (models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    ansType = models.IntegerField()
    # problemSet = models.ForeignKey('ProblemSet',db_column='problemSet')

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
    imageFilename = models.CharField(max_length=100)

    MULTI_CHOICE=1
    SHORT_ANSWER=0
    LONG_ANSWER=2
    UNLIMITED =0
    DIR_PREFIX ='surveyq_'

    class Meta:
        db_table = "prepostproblem"

    def isMultiChoice (self):
        return self.ansType==Question.MULTI_CHOICE

    def isShortAnswer (self):
        return self.ansType==Question.SHORT_ANSWER

    def isLongAnswer (self):
        return self.ansType==Question.LONG_ANSWER

    def isWaitUnlimited (self):
        return self.waitTimeSecs == Question.UNLIMITED

    def getDir (self):
        return 'surveyq_' + str(self.id)

    def toJSON (self):
        d = {"id": self.id}
        d['name'] = self.name
        d['description'] = self.description
        d['hoverText'] = self.hoverText
        return d


class Test (models.Model):
    name = models.CharField(max_length=100)
    isActive = models.BooleanField()
    questions = models.ManyToManyField(Question, through='TestQuestionMap')

    class Meta:
        db_table = "preposttest"

    def getQuestions (self):
        # return self.questions.order_by('position')
        return self.questions.order_by('link2Test')

    def addQuestion (self, q):
        c = self.questions.count()
        # uses 0-based positioning to add a new question to the map
        m = TestQuestionMap(test=self,question=q,position=c)
        m.save()

class TestQuestionMap (models.Model):
    question = models.ForeignKey(Question,db_column='probId', related_name='link2Test', on_delete=models.PROTECT)
    test = models.ForeignKey(Test,db_column='testId', on_delete=models.PROTECT)
    position = models.IntegerField()

    class Meta:
        db_table = "prepostproblemtestmap"
        ordering = ('position',)
        unique_together = (('question', 'test'),)  # workaround for there not being a single primary key