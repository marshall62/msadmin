from django.db import models


# A class used to hold all possible params and default values for an intervention selector
# This is used to populate pulldown menus so that user can only choose legal values for parameters.
from django.db.models.signals import post_init


# These objects form the model of a tutoring strategy.   There are two types of tutoring strategies: generic and
# actual.   All strategies are comprised of three strategy components (login, lesson, and tutor).  Each strategy component
# has parameters (sc_params).  A parameter is just a name-value pair which allows us to configure some settings
# on a strategy component.  A strategy component also contains several intervention selectors.  An intervention selector
# has parameters which are key-value pairs.

# The difference between an generic strategy and an actual strategy is that a generic strategy is defined
# as model of a strategy but isn't actually used by any class.  To make use of the generic strategy, a copy of
#  its structure is made and the resulting objects
# are what is an actual strategy.  All the classes below are used for both.   Instances are considered actual
# if they have a value in their myStrategy field.   If there is no value set for myStrategy, the object is generic.
# For convenience I've also added an isGeneric boolean on the Strategy class.

# Holds all the POSSIBLE parameters for an intervention selector.  The value field holds the default value
# of the parameter.   Generic only
class ISParamBase (models.Model):
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=1000)
    description = models.CharField(max_length=500)
    interventionSelector = models.ForeignKey('InterventionSelector',
                                             db_column='intervention_selector_id', on_delete=models.PROTECT)

    class Meta:
        db_table = "is_param_base"

    def getPossibleValues (self):
        vals = ISParamValue.objects.filter(isParam=self)
        return vals

    def __str__(self):
        selname = self.interventionSelector.name
        return selname + "::" + self.name + "=" + self.value


# Some ISParamBase have a set of legal values.  This holds one of the legal values for a param.
# Generic only
class ISParamValue (models.Model):
    isParam = models.ForeignKey(ISParamBase, db_column="isparamid",verbose_name="Base IS Param", on_delete=models.PROTECT)
    value = models.CharField(max_length=500)

    class Meta:
        db_table = "is_param_value"

    def __str__ (self):
        intsel = self.isParam.interventionSelector
        return intsel.name + ": " + self.isParam.name + "=" + self.value


# This is holds the actual param value used by a particular intervention selector in a particular
# strategy component
class InterventionSelectorParam(models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=1000)
    isActive = models.BooleanField()
    baseParam = models.ForeignKey(ISParamBase, db_column="paramid", on_delete=models.PROTECT)
    # aclass = models.ForgeignKey('Class',db_column="classid",null=True)
    # interventionSelector = models.ForeignKey('InterventionSelector',db_column="isid",on_delete=models.PROTECT)
    myStrategy = models.ForeignKey('Strategy',db_column='strategy_id', null=True,on_delete=models.PROTECT)
    scismap = models.ForeignKey('SCISMap', db_column="sc_is_map_id",verbose_name="StrategyComponent:InterventionSelector", on_delete=models.PROTECT)
    possibleValues = models.TextField(db_column='possible_values') # a CSV list of possible values that may be selected from for certain params
    description = models.CharField(max_length=500)

    @staticmethod
    def __makePossibleValsCSV (baseParam):
        vals = baseParam.getPossibleValues()
        if vals.count() > 0:
            poss_vals_csv = ""
            for v in vals:
                poss_vals_csv += v.value + ","
            return poss_vals_csv[0:-1]
        else: return None

    @staticmethod
    def getInstanceFromGenericParam (genericISParam, actualStrat):
        g=genericISParam
        self = InterventionSelectorParam()
        self.name = g.name
        self.value = g.value
        self.isActive = g.isActive
        self.myStrategy = actualStrat
        # self.baseParam = g.baseParam
        self.possibleValues = InterventionSelectorParam.__makePossibleValsCSV(g.baseParam)
        self.description = g.description
        return self

    @staticmethod
    def getInstanceFromActualParam (actualISParam, actualStrat):
        a=actualISParam
        self = InterventionSelectorParam()
        self.name = a.name
        self.value = a.value
        self.isActive = a.isActive
        self.myStrategy = actualStrat
        self.possibleValues = a.possibleValues
        self.description = a.description
        return self

    @staticmethod
    def getInstanceFromBaseParam (baseParam, actualStrat):
        self = InterventionSelectorParam()
        self.name = baseParam.name
        self.value = baseParam.value
        self.isActive = False
        self.myStrategy = actualStrat
        # self.baseParam = baseParam
        self.possibleValues = InterventionSelectorParam.__makePossibleValsCSV(baseParam)
        self.description = baseParam.description
        return self


    def getDescription (self):
        return self.description

    # return whats in the CSV string as a list of strings
    def getPossibleValues (self):
        if self.possibleValues:
            return self.possibleValues.split(',')
        else: return []


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

    def isActual (self):
        return self.myStrategy != None

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


    def __str__(self):
        isname = self.scismap.interventionSelector.name

        return isname + ":" + self.name + "=" + firstN(self.value,60)


#
class InterventionSelector(models.Model):

    LESSON="lesson"
    LOGIN="login"
    TUTOR="tutor"
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    onEvent = models.CharField(max_length=45)
    className = models.CharField(max_length=100)
    # config = models.TextField(blank=True)
    description = models.CharField(max_length=800,blank=True)
    briefDescription = models.CharField(max_length=120,blank=True)
    myStrategy =  models.ForeignKey('Strategy',db_column='strategy_id', null=True,blank=True,on_delete=models.PROTECT)
    type = models.CharField(max_length=10,choices=[(LOGIN,LOGIN),(LESSON,LESSON),(TUTOR,TUTOR) ])
    # actual intervention selectors hold a pointer to the generic parent
    genericParent = models.ForeignKey('InterventionSelector',db_column="generic_is_id", null=True,blank=True,on_delete=models.SET_NULL)


    # This creates an actual IS from a generic and is also be used to clone actual ISs.
    @staticmethod
    def getActual (genericIS, actualStrat):
        self = InterventionSelector()
        g = genericIS
        self.name = g.name
        self.onEvent = g.onEvent
        self.className = g.className
        # self.config = g.config
        self.description = g.description
        self.briefDescription = g.briefDescription
        self.myStrategy = actualStrat
        self.type = g.type
        self.genericParent = genericIS
        return self

    # uses the wayangoutpostdb.intervention_selector table
    class Meta:
        db_table = "intervention_selector"


    def __str__(self):
        if not self.myStrategy:
            parent = "Generic"
        else:
            parent = self.myStrategy.name
        return parent +":"+self.name

    def isActual (self):
        return self.myStrategy != None

    def getJSON (self, sc):
        # The active status of the IS is on the SCISMap
        isActive = self.getActiveStatus(sc)
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
        isParams = self.getParams(sc)
        for param in isParams:
            j = param.getJSON()
            jarr.append(j)

        d['children'] = jarr
        return d


    # The isActive status of the IS is held on the SCISMap
    def getActiveStatus (self, sc):
        # If this is an actual IS, get the SCISMap for this strategy
        if self.isActual():
            scismap= SCISMap.objects.filter(strategyComponent=sc, interventionSelector=self, myStrategy=self.myStrategy)
        else: scismap= SCISMap.objects.filter(strategyComponent=sc, interventionSelector=self)
        # It is possible that there is no mapping between SC and self in the given class if the
        # this intervention selector was added to the system after the time that the strategy (and this IS)
        # was set up for the class.   The desired behavior for class should not change and so we return the
        # active status of the IS as False
        if scismap.count() == 1:
            return scismap[0].isActive
        return False

    # def isActive (self, aclass, strategyComponent):
    #     return self.isActive

    # Gets the parameters of the intervention selector based on the strategy component.  This means
    # getting the isparam objects on the other end of the scismap connected to the interventionSelectorParam
    # (i.e. InterventionSelectorParam.scismap)
    def getParams (self, strategyComponent):
        # get the scsimap objecs that have both interventionSelector== self.id and strategyComponent==strategyComponent.id
        # This is done by filtering the interventionSelectorParams which connect to a scismap that has the IS and the SC with the right ids.
        params = InterventionSelectorParam.objects.filter(scismap__interventionSelector__pk=self.pk , scismap__strategyComponent__pk=strategyComponent.pk)
        return params.all()


    # Gets the parameters of the intervention selector
    def getAllParams (self, sc):
        res = [p for p in self.getParams(sc)]
        for p in self.getInactiveParams(sc):
            res.append(p)
        return res


    # Gets the base parameters for an intervention selecotr
    def getBaseParams (self):
        return ISParamBase.objects.filter(interventionSelector=self)

    # Returns a list of ISParamBase objects that are those base params that are not currently
    # used by the intervention selector
    def getInactiveParams (self, strategyComponent):
        baseParams = self.getBaseParams()
        usedParams = self.getParams(strategyComponent)
        inactiveParams = []
        for bp in baseParams:
            found = False
            for up in usedParams:
                if up.baseParam == bp:
                    found = True
                    break
            if not found:
                inactiveParams.append(bp)
        return inactiveParams


# A parameter of a strategy component.
class StrategyComponentParam (models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=200)
    description = models.CharField(max_length=800)
    isActive = models.BooleanField()
    myStrategy = models.ForeignKey('Strategy',db_column='strategy_id', null=True, blank=True, on_delete=models.PROTECT)

    @staticmethod
    def getActual ( genericSCParam, strat):
        self = StrategyComponentParam()
        g = genericSCParam
        self.name = g.name
        self.value = g.value
        self.description = g.description
        self.isActive = g.isActive
        self.myStrategy = strat
        return self

    class Meta:
        db_table = "sc_param"

    def __str__(self):
        maps = SCParamMap.objects.filter(param=self)
        if maps.count() > 0:
            scname = maps.first().strategyComponent.name
        else:
            scname = ""
        return scname + ":" + self.name + "=" + self.value

    def getJSON (self):

        d = {}
        d['title'] = self.name + '=' + self.value
        d['icon'] = 'glyphicon glyphicon-grain'
        d['type'] = 'scparam'
        d['isActive'] = 'true' if self.isActive else 'false'
        d['id'] = self.id
        return d



# A generic strategy has 3 strategy components: a login component, a lesson component, and a tutor component.
# An actual strategy component used by a class will have the strategy ID of the actual strategy.
class StrategyComponent(models.Model):
    LESSON="lesson"
    LOGIN="login"
    TUTOR="tutor"

    # id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    # className = models.CharField(max_length=100)
    className = models.CharField(max_length=100, null=True, blank=True, choices=[('edu.umass.ckc.wo.tutor.model.TopicModel','TopicModel'),
                                                          ('edu.umass.ckc.wo.tutor.model.CCLessonModel','CCLessonModel'),
                                                          ('edu.umass.ckc.wo.tutor.pedModel.BasePedagogicalModel', 'BasePedagogicalModel'),
                                                          ('edu.umass.ckc.wo.tutor.pedModel.SingleTopicPM','SingleTopicPedagogicalModel'),
                                                          ('None','None')])
    description = models.CharField(max_length=800)
    briefDescr = models.CharField(max_length=200)
    type = models.CharField(max_length=45, choices=[(InterventionSelector.LOGIN,
                                                     InterventionSelector.LOGIN),
                                                    (InterventionSelector.LESSON,
                                                     InterventionSelector.LESSON),
                                                    (InterventionSelector.TUTOR,
                                                     InterventionSelector.TUTOR) ])
    # supports the many-to-many relationship from StrategyComponent to InterventionSelector via the sc_is_map table
    interventionSelectors = models.ManyToManyField(InterventionSelector, through='SCISMap')
    # supports the many-to-many relationship from StrategyComponent to StrategyComponentParam via the sc_param_map
    params = models.ManyToManyField(StrategyComponentParam, through='SCParamMap')
    # strategy = models.ForeignKey('Strategy', db_column='strategy_id', null=True, on_delete=models.SET_NULL) # will have a value if this is part of an actual strategy
    is_generic = models.BooleanField(blank=True)

    def getParams (self):
        params = StrategyComponentParam.objects.filter(scparammap__strategyComponent=self)
        return params

    # Note this is used to create an actual from a generic and for partially cloning an actual SC
    @staticmethod
    def getActual ( genericSC):
        self = StrategyComponent()
        g = genericSC
        self.name = g.name
        self.className = g.className
        self.description = g.description
        self.briefDescr=g.briefDescr
        self.type = g.type
        self.is_generic = False
        return self


    #id = models.IntegerField(primary_key=True);

    class Meta:
        db_table = "strategy_component"


    def __str__(self):
        return self.name + (" <Generic>" if self.is_generic else " <Actual>")

    # return a dictionary
    def getJSON (self, aclass, strategy):
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

        inselarr = []
        for insel in self.interventionSelectors.all():
            j = insel.getJSON(self)
            inselarr.append(j)
        intervFolder['children'] = inselarr

        scparams = []
        for p in self.params.all():
            j = p.getJSON()
            scparams.append(j)
        scparamFolder['children'] = scparams
        return d




# An object that represents either a generic strategy or an actual strategy used by a class
class Strategy (models.Model):
    name = models.CharField(max_length=45)
    # THe use of the related_name is a response to a compile error.  I don't fully understand.
    lesson = models.ForeignKey(StrategyComponent,db_column='lesson_sc_id',related_name='StrategyLesson', null=True, on_delete=models.PROTECT)
    login = models.ForeignKey(StrategyComponent,db_column='login_sc_id',related_name='StrategyLogin', null=True, on_delete=models.PROTECT)
    tutor = models.ForeignKey(StrategyComponent,db_column='tutor_sc_id',related_name='StrategyTutor', null=True, on_delete=models.PROTECT)
    lc = models.ForeignKey('LC',db_column='lcid', blank=True, null=True, on_delete=models.PROTECT)
    description = models.TextField();
    aclass = models.ForeignKey('Class',db_column='classid',null=True,blank=True, on_delete=models.PROTECT) # will be null if generic strategy

    # Note: This is also used to make partial clones of actual strategies as well as generic ones
    @staticmethod
    def getActual (genericStrat, aclass):
        self = Strategy()
        g = genericStrat
        self.name = g.name
        self.lc = g.lc
        self.description = g.description
        self.aclass = aclass
        return self

    def isActual (self):
        return self.aclass != None

    # providing a getter to make sure bad chars like "\n" are not included which breaks the Javascript section of the
    # class_strategy2.html
    def getDescription (self):
        if self.description:
            descr= self.description.replace('\n','')
            descr= descr.replace('\r','')
            return descr
        else: return ''

    class Meta:
        db_table = "strategy"

    def __str__(self):
        return self.name

    def getSimpleJSON (self):
        d = {}
        d['id'] = self.pk
        d['name'] = self.name
        d['description'] = self.description
        return d

    def getJSON (self, aclass):

        j = [self.login.getJSON(aclass,self), self.lesson.getJSON(aclass,self),  self.tutor.getJSON(aclass,self)]
        return j







# Connects intervention selectors to their strategy component.
# Note:  WHen a new SCISMap is added to the system it is connecting an SC to an IS.  Often I forget to then connect
# all the necessary is_param_sc rows to this (there should be one for every is_param_base row).  It would be nice if the constructor
# of this class did that so that when I use the admin tool to connect an sc to an is, the is_param_sc get inserted, but I cannot
# figure out how to override the Model constructor.   They all break in various ways.
class SCISMap (models.Model):

    strategyComponent = models.ForeignKey(StrategyComponent, db_column="strategy_component_id", on_delete=models.PROTECT)
    interventionSelector = models.ForeignKey(InterventionSelector, db_column="intervention_selector_id", on_delete=models.PROTECT)
    config = models.TextField(db_column='config',blank=True)

    myStrategy = models.ForeignKey('Strategy', db_column='strategy_id',null=True,blank=True,on_delete=models.PROTECT)
    isActive = models.BooleanField()

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


def firstN (str,n):
    l = len(str)
    end = min(l,n)
    return str[0:n]


# Connects parameters to their strategy component
class SCParamMap (models.Model):
    strategyComponent = models.ForeignKey(StrategyComponent, db_column="strategy_component_id", on_delete=models.PROTECT)
    param = models.ForeignKey(StrategyComponentParam, db_column="sc_param_id", on_delete=models.PROTECT)
    myStrategy = models.ForeignKey('Strategy',db_column='strategy_id',blank=True,null=True,on_delete=models.PROTECT)
    is_active = models.BooleanField(blank=True)

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


class LC2Ruleset (models.Model):
    lc = models.ForeignKey("LC",db_column="lcid", on_delete=models.PROTECT)
    ruleset = models.ForeignKey("Ruleset",db_column="rulesetid", on_delete=models.PROTECT)
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








