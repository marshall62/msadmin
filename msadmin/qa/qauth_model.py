from django.db import models

class Problem (models.Model):
    name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=200)
    questType = models.CharField(max_length=45)
    statementHTML = models.TextField()
    audioResource = models.CharField(max_length=100) # deprecating in favor of audioFile below
    answer = models.TextField()
    imageURL = models.TextField(max_length=200)
    status = models.CharField(max_length=50)
    standardId = models.CharField(max_length=45)
    clusterId = models.CharField(max_length=45)
    form= models.CharField(max_length=50)
    layout = models.ForeignKey('ProblemLayout',db_column='layoutID')
    imageFile = models.ForeignKey('ProblemMediaFile',db_column='imageFileId',null=True)
    audioFile = models.ForeignKey('ProblemMediaFile',db_column='audioFileId',null=True)
    created_at = models.DateTimeField(db_column='createTimestamp', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='modTimestamp',auto_now=True)
    authorNotes = models.TextField()
    problemFormat = models.TextField()
    usableAsExample = models.BooleanField()
    # fields below here are being presented and may be edited but support is not elegant or FULL yet
    creator = models.TextField(max_length=50)  # should be an admin ID when login to system is implemented
    lastModifier = models.TextField(max_length=50) # should be an admin ID when login to system is implemented
    video = models.IntegerField() # this will require navigators & selectors.  Allow hand entry of video.ID now
    example = models.IntegerField() # this will require navigators & selectors.  Allow hand entry of problem.ID now
    # screenshotURL = models.CharField(max_length=200) # The filename living in MEDIA_ROOT/SNAPSHOT_DIRNAME/<filename>
                                                    # derived from the file upload of snapshotFile to json.py
    hasSnapshot = models.BooleanField()


    MULTI_CHOICE="multichoice"
    SHORT_ANSWER="shortanswer"
    DIR_PREFIX="problem_"

    def setFields (self, **kwargs):
        if kwargs is not None:
            if 'name' in kwargs:
                self.name = kwargs['name']
            if 'nickname' in kwargs:
                self.nickname = kwargs['nickname']
            if 'questType' in kwargs:
                self.questType = kwargs['questType']
            if 'statementHTML' in kwargs:
                self.statementHTML = kwargs['statementHTML']
            if 'answer' in kwargs:
                self.answer = kwargs['answer']
            if 'status' in kwargs:
                self.status = kwargs['status']
            if 'standardId' in kwargs:
                self.standardId = kwargs['standardId']
            if 'clusterId' in kwargs:
                self.clusterId = kwargs['clusterId']
            if 'form' in kwargs:
                self.form = kwargs['form']
            if 'layout_id' in kwargs:
                self.layout_id=kwargs['layout_id']
            if 'authorNotes' in kwargs:
                self.authorNotes=kwargs['authorNotes']
            if 'creator' in kwargs:
                self.creator=kwargs['creator']
            if 'lastModifier' in kwargs:
                self.lastModifier=kwargs['lastModifier']
            if 'example' in kwargs:
                self.example=kwargs['example']
            if 'video' in kwargs:
                self.video=kwargs['video']
            # if 'screenshotURL' in kwargs:
            #     self.screenshotURL=kwargs['screenshotURL']
            if 'usableAsExample' in kwargs:
                self.usableAsExample=kwargs['usableAsExample']
            if 'problemFormat' in kwargs:
                self.problemFormat=kwargs['problemFormat']
            if 'hasSnapshot' in kwargs:
                self.hasSnapshot=kwargs['hasSnapshot']


    class Meta:
        db_table = "problem"

    # def isReadAloud (self):
    #     return self.audioResource != None or self.audioFile != None

    def isMultiChoice (self):
        return self.questType==Problem.MULTI_CHOICE

    def getNumChoices (self):
        if self.isMultiChoice():
            return len(self.getAnswers())
        else:
            return 0

    def isShortAnswer (self):
        return self.questType==Problem.SHORT_ANSWER

    # def getReadAloud (self):
    #     return 'hasAudio' if self.isReadAloud() else 'noAudio'

    def getStatus3 (self):
        if self.status == 'ready' or self.status == 'testable':
            return self.status
        else:
            return 'dead'


    def getDifficulty (self):
        d = ProblemDifficulty.objects.get(problem_id=self.id)
        # I don't know what to do with this number
        if d and d.diff_level >= 0:
            l=d.diff_level * 10
        else:
            l=-1
        return str(int(l))


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

    def getProblemDir (self):
        return Problem.DIR_PREFIX + str(self.pk) + "/"

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

    # return the audioResource as a filename without the {[]} around it
    def getAudioFile (self):
        if len(self.audioResource) >= 4:
            return self.audioResource[2:-2]
        else:
            return self.audioResource


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

    @staticmethod
    def getProblemDirName (id):
        return Problem.DIR_PREFIX + str(id)


    def __str__ (self):
        return self.name

class ProblemDifficulty (models.Model):
    diff_level = models.FloatField(db_column="diff_level")
    problem = models.ForeignKey('Problem',db_column='problemId')

    class Meta:
        db_table = "overallprobdifficulty"

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
    imageURL = models.CharField(max_length=200)
    hoverText = models.CharField(max_length=200)
    order = models.IntegerField()
    givesAnswer = models.BooleanField()
    problem = models.ForeignKey('Problem',db_column='problemId')
    # The foreign key to the problem media table is allowed to be null
    imageFile = models.ForeignKey('ProblemMediaFile',db_column='imageFileId',null=True)
    audioFile = models.ForeignKey('ProblemMediaFile',db_column='audioFileId',null=True)
    placement = models.IntegerField() # 0,1,2

    DIR_PREFIX="hint_"

    class Meta:
        db_table = "hint"

    def __str__ (self):
        return str(self.pk) + ':' + self.name

    def getMediaFiles (self):
        files = ProblemMediaFile.objects.filter(hint=self)
        return files;

    @staticmethod
    def getHintDirName (id):
        return Hint.DIR_PREFIX + str(id)

    def toJSON (self):
        d = {}
        d['id'] = self.pk
        d['name'] = self.name
        d['statementHTML'] = self.statementHTML
        d['audioResource'] = self.audioResource # deprecating storage of audio file name in this field
        d['order'] = self.order
        d['hoverText'] = self.hoverText
        d['givesAnswer'] = self.givesAnswer
        d['imageURL'] = self.imageURL
        d['placement'] = self.placement
        if self.imageFile:
            d['imageFilename'] = self.imageFile.filename
            d['imageFileId'] = self.imageFile.id
        if self.audioFile:
            d['audioResource'] = self.audioFile.filename # overwrite audioResource with correct filename
            d['audioFileId'] = self.audioFile.id
        media = self.getMediaFiles()
        mfJSON = [m.toJSON() for m in media]
        d['mediaFiles'] = mfJSON
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
    hint = models.ForeignKey('Hint',db_column='hintId',null=True)

    class Meta:
        db_table = "problemmediafile"

    def toJSON (self):
        d = {}
        d['id'] = self.pk
        d['filename'] = self.filename
        d['probId'] = self.problem.pk
        if self.hint:
            d['hintId'] = self.hint.pk
        return d