from django.db import models

class Problem (models.Model):
    name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=200)
    questType = models.CharField(max_length=45)
    statementHTML = models.TextField()
    audioResource = models.CharField(max_length=100)
    answer = models.TextField()
    imageURL = models.TextField(max_length=100)
    status = models.CharField(max_length=50)
    standardId = models.CharField(max_length=45)
    clusterId = models.CharField(max_length=45)
    form= models.CharField(max_length=50)

    def setFields (self, **kwargs):
        if kwargs is not None:
            self.name = kwargs['name']
            self.nickname = kwargs['nickname']
            self.questType = kwargs['questType']
            self.statementHTML = kwargs['statementHTML']
            self.audioResource = kwargs['audioResource']
            self.answer = kwargs['answer']
            self.imageURL = kwargs['imageURL']
            self.status = kwargs['status']
            self.standardId = kwargs['standardId']
            self.clusterId = kwargs['clusterId']
            self.form = kwargs['form']


    class Meta:
        db_table = "problem"

    def isReadAloud (self):
        return self.audioResource == 'question'

    def getReadAloud (self):
        return 'hasAudio' if self.isReadAloud() else 'noAudio'

    def getStatus3 (self):
        if self.status == 'ready' or self.status == 'testable':
            return self.status
        else:
            return 'dead'


    # A static method to get all the quickAuth problems.  There's some inefficiency in this because we are going
    # call this alot and its going to get all the problems from the db.
    @staticmethod
    def get_quickAuth_problems ():
        return Problem.objects.filter(form='quickAuth')

    def __str__ (self):
        return self.name

class Hint (models.Model):
    name = models.CharField(max_length=100)
    statementHTML = models.TextField()
    audioResource = models.CharField(max_length=100)
    hoverText = models.CharField(max_length=200)
    order = models.IntegerField()
    givesAnswer = models.BooleanField()
    problem = models.ForeignKey('Problem',db_column='problemId')

    class Meta:
        db_table = "hint"

    def __str__ (self):
        return self.name
