from django.db import models
from .submodel import machine_model
from .submodel import qauth_model

# A class used to hold all possible params and default values for an intervention selector
# This is used to populate pulldown menus so that user can only choose legal values for parameters.
from django.db.models.signals import post_init


class ISParamBase (models.Model):
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=1000)
    description = models.CharField(max_length=500)
    interventionSelector = models.ForeignKey('InterventionSelector',db_column='intervention_selector_id')

    class Meta:
        db_table = "is_param_base"

    def getPossibleValues (self):
        vals = ISParamValue.objects.filter(isParam=self)
        return vals

    def __str__(self):
        selname = self.interventionSelector.name
        return selname + "::" + self.name + "=" + self.value


class InterventionSelector(models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    onEvent = models.CharField(max_length=45)
    className = models.CharField(max_length=100)
    config = models.TextField(blank=True)
    description = models.CharField(max_length=800)
    briefDescription = models.CharField(max_length=120)


    # uses the wayangoutpostdb.intervention_selector table
    class Meta:
        db_table = "intervention_selector"


    def __str__(self):
        return self.name

    def getJSON (self, sc, aclass, classSC):
        # One field in the JSON is determined based on class and SC.   This is because the class_sc_is_map holds the status
        # of whether the intervention selector is active or not.   So this sets a local isActive which is then included in the JSON
        isActive = self.setActiveStatus(aclass,sc,classSC)
        d = {}
        d['title'] = self.name
        d['type'] = 'interventionSelector'
        d['id'] = self.id
        d['icon'] = "glyphicon glyphicon-modal-window"
        d['scId'] = sc.id
        # d['isActive'] = 'true' if self.isActive(aclass,sc) else 'false'
        d['isActive'] = 'true' if isActive else 'false'
        d['tooltip'] = self.briefDescription if self.briefDescription else self.description
        jarr = []
        # We need to find all the is-param-base objects for this IS and then round up the is-param-class objects from them.
        for bp in ISParamBase.objects.filter(interventionSelector=self):
            # print("getting is-param-class for class=" + str(aclass.id) + " param=" + str(bp.id) )
            p = ClassISParam.objects.get(theClass=aclass, isParam=bp, classSC=classSC)
            j = p.getJSON()
            jarr.append(j)
        # old way - no longer works
        # for p in self.getClassParams(sc,aclass):
        #     j = p.getJSON()
        #     jarr.append(j)
        d['children'] = jarr
        return d

    # This is called just before rendering a view that shows this intervention selector.
    #  It sets its status based on the class_sc_is_map which holds switches that turn on/off ISs
    def setActiveStatus (self, aclass, sc, classSC):
        scismap= SCISMap.objects.get(strategyComponent=sc, interventionSelector=self)
        cscismap = ClassSCISMap.objects.get(theClass=aclass,ismap=scismap, classSC=classSC)
        isActive = cscismap.isActive
        return isActive

    # def isActive (self, aclass, strategyComponent):
    #     return self.isActive

    # Gets the parameters of the intervention selector based on the strategy component.  This means
    # getting the isparam objects on the other end of the scismap connected to the interventionSelectorParam
    # (i.e. InterventionSelectorParam.scismap)
    def getParams (self, strategyComponent):
        # get the scsimap objecs that have both interventionSelector== self.id and strategyComponent==strategyComponent.id
        # This is done by filtering the interventionSelectorParams which connect to a scismap that has the IS and the SC with the right ids.
        params = InterventionSelectorParam.objects.filter(scismap__interventionSelector__pk=self.pk , scismap__strategyComponent__pk=strategyComponent.pk)
        return params


    def getClassParams (self, sc, aclass):
        # get the scsimap objecs that have both interventionSelector== self.id and strategyComponent==strategyComponent.id
        # This is done by filtering the interventionSelectorParams which connect to a scismap that has the IS and the SC with the right ids.
        # sc_params = InterventionSelectorParam.objects.filter(scismap__interventionSelector__pk=self.pk , scismap__strategyComponent__pk=strategyComponent.pk)
        baseParams = ISParamBase.objects.filter(interventionSelector=self)
        classParams = []
        for bp in baseParams:
            # TODO we've hit a bug here when the get returns more than one object.   This can happen when a particular class uses strategies
            # that include the same intervention selector more than once and the is-param is part of that insel AND it is NOT connected to an
            # is-param-sc (i.e. the scisParam field is None).  The scisParam field is None because the is-param-class object was created from the is-param-base
            # object and not an is-param-sc object.   So if there are two or more such is-param-class objects, it will be impossible to distinguish them.
            cp = ClassISParam.objects.get(isParam=bp, scisParam=sc, theClass=aclass)
            classParams.append(cp)
        return classParams


    # Gets the base parameters for an intervention selecotr
    def getBaseParams (self):
        return ISParamBase.objects.filter(interventionSelector=self)

class StrategyComponentParam (models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=200)
    description = models.CharField(max_length=800)

    class Meta:
        db_table = "sc_param"

    def __str__(self):
        return self.name + "=" + self.value

    def getJSON (self, aclass, classSC):
        # print("getJSON for " + str(self))
        cp = ClassSCParam.objects.get(scParam=self,theClass=aclass, classSC=classSC)
        d = {}
        d['title'] = self.name + '=' + cp.value
        d['icon'] = 'glyphicon glyphicon-grain'
        d['type'] = 'scparam'
        d['isActive'] = 'true' if cp.isActive else 'false'
        d['id'] = cp.id
        return d



class StrategyComponent(models.Model):
    LESSON="lesson"
    LOGIN="login"
    TUTOR="tutor"

    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    # className = models.CharField(max_length=100)
    className = models.CharField(max_length=100, choices=[('edu.umass.ckc.wo.tutor.model.TopicModel','TopicModel'),
                                                          ('edu.umass.ckc.wo.tutor.model.CCLessonModel','CCLessonModel'),
                                                          ('edu.umass.ckc.wo.tutor.pedModel.BasePedagogicalModel', 'BasePedagogicalModel'),
                                                          ('edu.umass.ckc.wo.tutor.pedModel.SingleTopicPM','SingleTopicPedagogicalModel'),
                                                          ('None','None')])
    description = models.CharField(max_length=800)
    briefDescr = models.CharField(max_length=200)
    type = models.CharField(max_length=45, choices=[(LOGIN,LOGIN),(LESSON,LESSON),(TUTOR,TUTOR) ])
    # supports the many-to-many relationship from StrategyComponent to InterventionSelector via the sc_is_map table
    interventionSelectors = models.ManyToManyField(InterventionSelector, through='SCISMap')
    # supports the many-to-many relationship from StrategyComponent to StrategyComponentParam via the sc_param_map
    params = models.ManyToManyField(StrategyComponentParam, through='SCParamMap')



    #id = models.IntegerField(primary_key=True);

    class Meta:
        db_table = "strategy_component"


    def __str__(self):
        return self.name

    # return a dictionary
    def getJSON (self, aclass, classStrategy):
        d = {}
        d ['title'] = self.name
        d ['icon'] = "glyphicon glyphicon-king"
        d['unselectable'] = 'true' # disables the checkbox
        intervFolder = {}
        intervFolder['title'] = 'Interventions'
        intervFolder['unselectable'] = 'true' # disables the checkbox
        intervFolder['icon'] = "glyphicon glyphicon-equalizer"
        scparamFolder = {}
        scparamFolder['title'] = 'Parameters'
        scparamFolder['unselectable'] = 'true' # disables the checkbox
        scparamFolder['icon'] = "glyphicon glyphicon-tree-conifer"
        folders = [intervFolder, scparamFolder]
        d['children'] = folders
        clSC = SC_Class.objects.get(theClass=aclass,sc=self,classStrategy=classStrategy)
        inselarr = []
        for insel in self.interventionSelectors.all():
            j = insel.getJSON(self,aclass,clSC)
            inselarr.append(j)
        intervFolder['children'] = inselarr
        scparams = []
        for p in self.params.all():
            j = p.getJSON(aclass,clSC)
            scparams.append(j)
        scparamFolder['children'] = scparams
        return d




    # return a query set of intervention selectors that are in this strategy
    # def getInterventionSelectors (self):
    #     sels = InterventionSelector.objects.filter(scismap__strategyComponent=self.id)
    #     return sels

    # return a query set of parameters that are in this strategy
    # def getParams (self):
    #     params = StrategyComponentParam.objects.filter(scparammap__strategyComponent=self.id)
    #     return params


class Strategy (models.Model):
    name = models.CharField(max_length=45)
    # THe use of the related_name is a response to a compile error.  I don't fully understand.
    lesson = models.ForeignKey(StrategyComponent,db_column='lesson_sc_id',related_name='StrategyLesson')
    login = models.ForeignKey(StrategyComponent,db_column='login_sc_id',related_name='StrategyLogin')
    tutor = models.ForeignKey(StrategyComponent,db_column='tutor_sc_id',related_name='StrategyTutor')
    lc = models.ForeignKey('LC',db_column='lcid')
    description = models.TextField();

    class Meta:
        db_table = "strategy"

    def __str__(self):
        return self.name

    def getJSON (self, aclass):
        strat = Strategy_Class.objects.get(strategy=self, theClass=aclass)
        j = [self.login.getJSON(aclass,strat), self.lesson.getJSON(aclass,strat),  self.tutor.getJSON(aclass,strat)]
        return j


#  TODO Need to be able to change the learning companion that is assigned to the strategy for a class.
class Strategy_Class (models.Model):
    # Note:  A custom strategy made from components will not refer to a strategy it can be None (or null in the strategyId column)
    strategy = models.ForeignKey(Strategy, db_column="strategyId", null=True)
    theClass = models.ForeignKey('Class', db_column="classId")
    lc = models.ForeignKey('LC',db_column='lcid')
    name = models.CharField(max_length=60)
    description = models.TextField();


    class Meta:
        db_table = "strategy_class"

    def getSimpleJSON (self) :
        d = {}
        d['name'] = self.name
        d['id'] = self.pk
        return d



    def getJSON (self):
        # get the SC_Class objects that go with this strategy-class (there should be 3 scs: login,lesson,tutor)
        scs = SC_Class.objects.filter(classStrategy=self)
        loginsc = lessonsc = tutorsc = None
        for sc in scs:
            if sc.sc.type == StrategyComponent.LOGIN:
                loginsc = sc
            elif sc.sc.type == StrategyComponent.LESSON:
                lessonsc = sc
            else:
                tutorsc = sc

        j = [loginsc.getJSON(self), lessonsc.getJSON(self),  tutorsc.getJSON(self)]
        return j


class SC_Class (models.Model):
    theClass = models.ForeignKey('Class', db_column='classId')
    sc = models.ForeignKey(StrategyComponent, db_column='scId')
    classStrategy = models.ForeignKey('Strategy_Class', db_column="strategy_class_id")

    class Meta:
        db_table = "sc_class"

    # return a dictionary
    def getJSON (self, classStrategy):
        d = {}
        d ['title'] = self.sc.name
        d ['icon'] = "glyphicon glyphicon-king"
        d['unselectable'] = 'true' # disables the checkbox
        intervFolder = {}
        intervFolder['title'] = 'Interventions'
        intervFolder['unselectable'] = 'true' # disables the checkbox
        intervFolder['icon'] = "glyphicon glyphicon-equalizer"
        scparamFolder = {}
        scparamFolder['title'] = 'Parameters'
        scparamFolder['unselectable'] = 'true' # disables the checkbox
        scparamFolder['icon'] = "glyphicon glyphicon-tree-conifer"
        folders = [intervFolder, scparamFolder]
        d['children'] = folders
        inselarr = []
        for insel in self.sc.interventionSelectors.all():
            j = insel.getJSON(self.sc,self.theClass,self)
            inselarr.append(j)
        intervFolder['children'] = inselarr
        scparams = []
        for p in self.sc.params.all():
            j = p.getJSON(self.theClass,self)
            scparams.append(j)
        scparamFolder['children'] = scparams
        return d


# This isn't quite right because it connects a param to an intervention selector. We need to create
# a param for the intervention selector within each strategy component where the intervention selector is used.
# Therefore we use the model below
# class InterventionSelectorParam(models.Model):
#     # id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=45)
#     value = models.CharField(max_length=200)
#     interventionSelector = models.ForeignKey(InterventionSelector, db_column="intervention_selector_id")
#
#     class Meta:
#         db_table = "is_param"
#
#     def __str__(self):
#         return self.name + "=" + self.value




# Note:  WHen a new SCISMap is added to the system it is connecting an SC to an IS.  Often I forget to then connect
# all the necessary is_param_sc rows to this (there should be one for every is_param_base row).  It would be nice if the constructor
# of this class did that so that when I use the admin tool to connect an sc to an is, the is_param_sc get inserted, but I cannot
# figure out how to override the Model constructor.   They all break in various ways.
class SCISMap (models.Model):

    strategyComponent = models.ForeignKey(StrategyComponent, db_column="strategy_component_id")
    interventionSelector = models.ForeignKey(InterventionSelector, db_column="intervention_selector_id")
    config = models.TextField(db_column='config',blank=True)

    # def __init__ (self, *args, **kwargs):
    #     print("hi")
    #     super().__init__(args,kwargs)
    #     print('bye')



    class Meta:
        db_table = "sc_is_map"



    def __str__(self):
        return self.strategyComponent.__str__() + ":" + self.interventionSelector.__str__()

    # return the list of is-param-sc objects associated with this.
    def getISParams (self):
        return InterventionSelectorParam.objects.filter(scismap=self)

# This handles a signal from django after it runs its SCIS constructor.
# def extraSCISInit (**kwargs):
#     print("in My SCIS extra init ")
#     instance = kwargs.get('instance')
    # print("SCIS ID " + instance.id)
    # if instance.strategyComponent != None:
    #     print("I have an sc")
    # else:
    #     print("I have no sc")
    # instance = kwargs.get('instance')
    # print(instance)
    # sc = kwargs.get('strategyComponent')
    # print(sc)


# post_init.connect(extraSCISInit, SCISMap)

# This is the actual param value used by a particular intervention selector in a particular
# strat component
class InterventionSelectorParam(models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=1000)
    isActive = models.BooleanField()
    baseParam = models.ForeignKey(ISParamBase, db_column="paramid")
    scismap = models.ForeignKey(SCISMap, db_column="sc_is_map_id",verbose_name="StrategyComponent:InterventionSelector")

    def getPossibleValues (self):
        return self.baseParam.getPossibleValues()


    # provide a constructor so that I can add in my own properties
    # def __init__(self, *args, **kwargs):
    #     super(models.Model, self).__init__(*args, **kwargs)
    #     self.isName = self.scismap.interventionSelector.name

    # This is a way of giving the class further properties beside the db fields.
    # I want the admin form to be able to sort these objects based on the name of the intervention selector associated
    # with this object.  This decorator (?) will allow me to use obj.isName  (not obj.isName() ) to get this value.
    # @property
    # def isName (self):
    #     # set a default value if not bound
    #     if not hasattr(self, '_isName'):
    #         self._isName = self.scismap.interventionSelector.name
    #     # return getattr(self, '_isName', self.scismap.interventionSelector.name)  # alternative to above 2 lines
    #     return self._isName

    class Meta:
        db_table = "is_param_sc"



    # TODO would like to be able to have a name like CollabLogin.Pretest: runFreq = oncePerSession  (maybe first 20 chars of the value)
    # This would require some kind of query thru the SCISMap FK to get the strategy component and the intervention selector
    def __str__(self):
        #m = SCISMap.objects.get(interventionSelector=self.id)
        sel = self.scismap.interventionSelector
        sc = self.scismap.strategyComponent
        scname = sc.name
        isname = sel.name
        return  isname + " : " + self.name + "=" + firstN(self.value,60) + " (sc=" + str(self.id) + ":" + scname + ")"

def firstN (str,n):
    l = len(str)
    end = min(l,n)
    return str[0:n]

class SCParamMap (models.Model):
    strategyComponent = models.ForeignKey(StrategyComponent, db_column="strategy_component_id")
    param = models.ForeignKey(StrategyComponentParam, db_column="sc_param_id")

    class Meta:
        db_table = "sc_param_map"

    def __str__(self):
        return self.strategyComponent.__str__() + ":" + self.param.__str__()


class Class (models.Model):
    name = models.CharField(max_length=50)
    teacher = models.CharField(max_length=50)
    # strategies = models.ManyToManyField(Strategy, through='ClassStrategyMap')
    teacherId = models.IntegerField()

    class Meta:
        db_table = "class"

    def __str__ (self):
        return self.teacher + ": " + self.name

    def toJSON (self):
        d = {}
        d['id'] = self.pk
        d['teacher'] = self.teacher
        d['teacherId'] = self.teacherId
        d['name'] = self.name
        return d






class Teacher (models.Model):

    fname = models.CharField(max_length=50,db_column='fname')
    lname = models.CharField(max_length=50,db_column='lname')

    class Meta:
        db_table = "teacher"

    def __str__ (self):
        return str(self.fname) + str(self.lname)

'''
Django Composite Key might be a solution for you:

https://github.com/simone/django-compositekey
'''

class ClassSCParam (models.Model):
    scParam = models.ForeignKey(StrategyComponentParam, db_column="sc_param_id",verbose_name="Strategy Component Param")
    theClass = models.ForeignKey(Class, db_column="classId",verbose_name="Class")
    classSC = models.ForeignKey(SC_Class, db_column="sc_class_id", verbose_name="Class Strategy Component")
    isActive = models.BooleanField()
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=200)

    class Meta:
        db_table = "class_sc_param"

    def __str__ (self):
        return str(self.theClass.name) + ":" + self.classSC.sc.name + "::" + self.name + "=" + self.value

class ClassISParam (models.Model):
    isParam = models.ForeignKey(ISParamBase, db_column="is_param_id",verbose_name="Intervention Selector Param")
    # Defined to allow Null in this fk
    scisParam = models.ForeignKey(InterventionSelectorParam, db_column="scis_param_id",verbose_name="Intervention Selector Param")
    theClass = models.ForeignKey(Class, db_column="classId", verbose_name="Class")
    classSC = models.ForeignKey(SC_Class, db_column="sc_class_id", verbose_name="Class Strategy Component")
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=1000)
    isActive = models.BooleanField(db_column='isActive')

    # def getPossibleValues (self):
    #     return self.isParam.getPossibleValues()

    def getPossibleValues (self):
        return self.isParam.getPossibleValues()

    # def name (self):
    #     return self.isParam.name

    class Meta:
        db_table = "is_param_class"

    def __str__ (self):
        return str(self.theClass.name) + ":" + self.isParam.interventionSelector.name + "::" + self.name + "=" + self.value

    def getJSON (self):
        d = {}
        d["title"] = self.name + "=" +  self.value
        d["id"] = str(self.id)
        d["icon"] = "glyphicon glyphicon-leaf"
        # d["isActive"] = str(self.isActive)
        d["isActive"] = self.isActive
        # fancytree will turn on the checkbox next to a node if it has a selected=true setting
        if self.isActive:
            d["selected"] = 'true'
        d["type"] = 'param'
        # d['extraClasses'] = 'is-param' # a style element exists in the CSS to color the glyphicon based on this
        return d

class ClassSCISMap (models.Model):
    ismap = models.ForeignKey(SCISMap, db_column="sc_is_map_id", verbose_name="Strategy Component: Intervention Selector")
    theClass = models.ForeignKey(Class, db_column="classId", verbose_name="Class")
    isActive = models.BooleanField()
    config = models.TextField()
    classSC = models.ForeignKey(SC_Class, db_column="sc_class_id", verbose_name="Class SC")

    class Meta:
        db_table = "class_sc_is_map"

    def __str__ (self):
        return str(self.theClass.name) + ":" + self.ismap.strategyComponent.name + "::" + self.ismap.interventionSelector.name

# Some Base ISParams have legal values.  This is a record of a legal value for a param.
class ISParamValue (models.Model):
    isParam = models.ForeignKey(ISParamBase, db_column="isparamid",verbose_name="Base IS Param")
    value = models.CharField(max_length=500)

    class Meta:
        db_table = "is_param_value"

    def __str__ (self):
        intsel = self.isParam.interventionSelector
        return intsel.name + ": " + self.isParam.name + "=" + self.value

class LC2Ruleset (models.Model):
    lc = models.ForeignKey("LC",db_column="lcid")
    ruleset = models.ForeignKey("Ruleset",db_column="rulesetid")
    class Meta:
        db_table="lc_ruleset_map"

class Ruleset (models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "ruleset"

    def __str__ (self):
        return self.name

class LC (models.Model):
    name = models.CharField(max_length=45)
    className = models.CharField(max_length=200,choices=[('edu.umass.ckc.wo.tutor.agent.JaneNoEmpathicLC','JaneNoEmpathicLC'),
                                                                          ('edu.umass.ckc.wo.tutor.agent.JaneSemiEmpathicLC','JaneSemiEmpathicLC'),
                                                                          ('edu.umass.ckc.wo.tutor.agent.JaneEmpathicLC','JaneEmpathicLC'),
                                                                          ('edu.umass.ckc.wo.tutor.agent.JakeNoEmpathicLC','JakeNoEmpathicLC'),
                                                                          ('edu.umass.ckc.wo.tutor.agent.JakeSemiEmpathicLC','JakeSemiEmpathicLC'),
                                                                          ('edu.umass.ckc.wo.tutor.agent.JakeEmpathicLC','JakeEmpathicLC'),
                                                                          ('edu.umass.ckc.wo.tutor.agent.RuleDrivenLearningCompanion','RuleDrivenLearningCompanion')])
    charName = models.CharField(max_length=45)
    rulesets = models.ManyToManyField(Ruleset,through="LC2Ruleset")
    description = models.TextField()

    class Meta:
        db_table = "lc"

    def __str__ (self):
        return self.name + ": " + self.charName








