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
    layout = models.ForeignKey('ProblemLayout',db_column='layoutID')

    MULTI_CHOICE="multichoice"
    SHORT_ANSWER="shortanswer"

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
            self.layout_id=kwargs['layout_id']


    class Meta:
        db_table = "problem"

    def isReadAloud (self):
        return self.audioResource == 'question'

    def isMultiChoice (self):
        return self.questType==Problem.MULTI_CHOICE

    def getNumChoices (self):
        if self.isMultiChoice():
            return len(self.getAnswers())
        else:
            return 0

    def isShortAnswer (self):
        return self.questType==Problem.SHORT_ANSWER

    def getReadAloud (self):
        return 'hasAudio' if self.isReadAloud() else 'noAudio'

    def getStatus3 (self):
        if self.status == 'ready' or self.status == 'testable':
            return self.status
        else:
            return 'dead'

    def getLayoutId (self):
        if self.layout:
            return self.layout.id
        else:
            return -1

    def getLayoutName (self):
        if self.layout:
            return self.layout.name
        else:
            return ''

    def getLayoutDescription (self):
        if self.layout:
            return self.layout.description
        else:
            return ''

    def getHints (self):
        hints = Hint.objects.filter(problem=self)
        return hints

    def getAnswers (self):
        answers = ProblemAnswer.objects.filter(problem=self).order_by('order')
        anslist = [ x for x in answers]
        # THere is some inconsistency in quickAuth in that it allows the Problem.answer field to be a lone answer to a shortanswer
        # problem OR it will look in the problemAnswers table for one or more.  In our GUI we want to hide this issue
        # and so we put the lone answer from problem.answer into the list of answers.
        if self.isShortAnswer() and self.answer and anslist == []:
            loneAns = ProblemAnswer(val=self.answer)
            anslist.append(loneAns)
        return anslist

    def getMediaFiles (self):
        files = ProblemMediaFile.objects.filter(problem=self)
        return files;

    # Because the imageURL is stored in the db as {[myimage.jpg]} or http://somepath/myimage.jpg we need to return
    # just myimage.jpg in the first case.
    def getImageURL (self):
        if self.imageURL.find('{[') == 0:
            return self.imageURL[2:-2]
        else:
            return self.imageURL


    def toJSON (self):
        d = {}
        d['id'] = self.pk
        d['name'] = self.name
        d['questType'] = self.questType
        d['isMultiChoice'] = self.isMultiChoice()
        d['isShortAnswer'] = self.isShortAnswer()
        l = self.getAnswers()
        d['answers'] = [a.toJSON() for a in self.getAnswers()]

        d['answer'] = self.answer
        d['numHints'] = len(self.getHints())
        return d


    # A static method to get all the quickAuth problems.  There's some inefficiency in this because we are going
    # call this alot and its going to get all the problems from the db.
    @staticmethod
    def get_quickAuth_problems ():
        return Problem.objects.filter(form='quickAuth')

    def __str__ (self):
        return self.name


class ProblemAnswer (models.Model):
    val = models.TextField()
    choiceLetter = models.CharField(max_length=1)
    hintText = models.CharField(max_length=200)
    order = models.IntegerField()
    bindingPosition = models.IntegerField()
    problem = models.ForeignKey('Problem',db_column='probId')

    class Meta:
        db_table = "problemanswers"

    def toJSON (self) :
        d = {}
        d['id'] = self.pk
        d['val'] = self.val
        d['choiceLetter'] = self.choiceLetter
        return d


class Hint (models.Model):
    name = models.CharField(max_length=100)
    statementHTML = models.TextField()
    audioResource = models.CharField(max_length=100)
    imageURL = models.CharField(max_length=100)
    hoverText = models.CharField(max_length=200)
    order = models.IntegerField()
    givesAnswer = models.BooleanField()
    problem = models.ForeignKey('Problem',db_column='problemId')

    class Meta:
        db_table = "hint"

    def __str__ (self):
        return self.name

    def toJSON (self):
        d = {}
        d['id'] = self.pk
        d['name'] = self.name
        d['statementHTML'] = self.statementHTML
        d['audioResource'] = self.audioResource
        d['order'] = self.order
        d['hoverText'] = self.hoverText
        d['givesAnswer'] = self.givesAnswer
        d['imageURL'] = self.imageURL
        return d

class ProblemLayout (models.Model):
    problemFormat = models.TextField()
    name = models.CharField(max_length=45)
    notes = models.CharField(max_length=100)
    description = models.CharField(max_length=150)

    class Meta:
        db_table = "problemlayout"

    def toJSON (self):
        d = {}
        d['id'] = self.pk
        d['name'] = self.name
        d['description'] = self.description
        return d

class ProblemMediaFile (models.Model):
    filename = models.CharField(max_length=100)
    problem = models.ForeignKey('Problem',db_column='probId')

    class Meta:
        db_table = "problemmediafile"

    def toJSON (self):
        d = {}
        d['id'] = self.pk
        d['filename'] = self.filename
        return d