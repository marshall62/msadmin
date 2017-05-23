from django.db import models

# A class used to hold all possible params and default values for an intervention selector
class ISParamBase (models.Model):
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=1000)
    interventionSelector = models.ForeignKey('InterventionSelector',db_column='intervention_selector_id')

    class Meta:
        db_table = "is_param_base"

    def possibleValues (self):
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


    # uses the wayangoutpostdb.intervention_selector table
    class Meta:
        db_table = "intervention_selector"


    def __str__(self):
        return self.name

    # This is called just before rendering a view that shows this intervention selector.
    #  It sets its status based on the class_sc_is_map which holds switches that turn on/off ISs
    def setActiveStatus (self, aclass, sc):
        scismap= SCISMap.objects.get(strategyComponent=sc, interventionSelector=self)
        cscismap = ClassSCISMap.objects.get(theClass=aclass,ismap=scismap)
        self.isActive = cscismap.isActive
        return self.isActive

    def isActive (self, aclass, strategyComponent):
        return self.isActive

    # Gets the parameters of the intervention selector based on the strategy component.  This means
    # getting the isparam objects on the other end of the scismap connected to the interventionSelectorParam
    # (i.e. InterventionSelectorParam.scismap)
    def getParams (self, strategyComponent):
        # get the scsimap objecs that have both interventionSelector== self.id and strategyComponent==strategyComponent.id
        # This is done by filtering the interventionSelectorParams which connect to a scismap that has the IS and the SC with the right ids.
        params = InterventionSelectorParam.objects.filter(scismap__interventionSelector__pk=self.pk , scismap__strategyComponent__pk=strategyComponent.pk)
        return params

    # Gets the base parameters for an intervention selecotr
    def getBaseParams (self):
        return ISParamBase.objects.filter(interventionSelector=self)

class StrategyComponentParam (models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=200)

    class Meta:
        db_table = "sc_param"

    def __str__(self):
        return self.name + "=" + self.value


class StrategyComponent(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    className = models.CharField(max_length=100)
    # supports the many-to-many relationship from StrategyComponent to InterventionSelector via the sc_is_map table
    interventionSelectors = models.ManyToManyField(InterventionSelector, through='SCISMap')
    # supports the many-to-many relationship from StrategyComponent to StrategyComponentParam via the sc_param_map
    params = models.ManyToManyField(StrategyComponentParam, through='SCParamMap')

    #id = models.IntegerField(primary_key=True);

    class Meta:
        db_table = "strategy_component"

    def publish (self):
        self.save()

    def __str__(self):
        return self.name

    # return a query set of intervention selectors that are in this strategy
    def getInterventionSelectors (self):
        sels = InterventionSelector.objects.filter(scismap__strategyComponent=self.id)
        return sels

    # return a query set of parameters that are in this strategy
    def getParams (self):
        params = StrategyComponentParam.objects.filter(scparammap__strategyComponent=self.id)
        return params


class Strategy (models.Model):
    name = models.CharField(max_length=45)
    # THe use of the related_name is a response to a compile error.  I don't fully understand.
    lesson = models.ForeignKey(StrategyComponent,db_column='lesson_sc_id',related_name='StrategyLesson')
    login = models.ForeignKey(StrategyComponent,db_column='login_sc_id',related_name='StrategyLogin')
    tutor = models.ForeignKey(StrategyComponent,db_column='tutor_sc_id',related_name='StrategyTutor')

    class Meta:
        db_table = "strategy"

    def __str__(self):
        return self.name


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




class SCISMap (models.Model):

    strategyComponent = models.ForeignKey(StrategyComponent, db_column="strategy_component_id")
    interventionSelector = models.ForeignKey(InterventionSelector, db_column="intervention_selector_id")
    config = models.TextField(db_column='config',blank=True)

    class Meta:
        db_table = "sc_is_map"



    def __str__(self):
        return self.strategyComponent.__str__() + ":" + self.interventionSelector.__str__()


# This is the actual param value used by a particular intervention selector in a particular
# strat component
class InterventionSelectorParam(models.Model):
    # id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=1000)
    baseParam = models.ForeignKey(ISParamBase, db_column="paramid")
    scismap = models.ForeignKey(SCISMap, db_column="sc_is_map_id",verbose_name="StrategyComponent:InterventionSelector")


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

    def name (self):
        return self.baseParam.name

    # TODO would like to be able to have a name like CollabLogin.Pretest: runFreq = oncePerSession  (maybe first 20 chars of the value)
    # This would require some kind of query thru the SCISMap FK to get the strategy component and the intervention selector
    def __str__(self):
        #m = SCISMap.objects.get(interventionSelector=self.id)
        sel = self.scismap.interventionSelector
        sc = self.scismap.strategyComponent
        scname = sc.name
        isname = sel.name
        return  str(self.id) + " " + scname+"."+isname + " : " + self.name() + "=" + self.value


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
    strategies = models.ManyToManyField(Strategy, through='ClassStrategyMap')

    class Meta:
        db_table = "class"

    def __str__ (self):
        return self.teacher + ": " + self.name

class ClassStrategyMap (models.Model):
    myclass = models.ForeignKey(Class,db_column='classId')
    strategy = models.ForeignKey(Strategy,db_column='strategyId')

    class Meta:
        db_table = "class_strategy_map"

    def __str__ (self):
        return str(self.myclass) + str(self.strategy)


'''
Django Composite Key might be a solution for you:

https://github.com/simone/django-compositekey
'''

class ClassSCParam (models.Model):
    scParam = models.ForeignKey(StrategyComponentParam, db_column="sc_param_id",verbose_name="Strategy Component Param")
    theClass = models.ForeignKey(Class, db_column="classId",verbose_name="Class")
    value = models.CharField(max_length=200)

    class Meta:
        db_table = "class_sc_param"

class ClassISParam (models.Model):
    # isParam = models.ForeignKey(InterventionSelectorParam, db_column="is_param_id",verbose_name="Intervention Selector Param")
    isParam = models.ForeignKey(ISParamBase, db_column="is_param_id",verbose_name="Intervention Selector Param")
    theClass = models.ForeignKey(Class, db_column="classId", verbose_name="Class")
    value = models.CharField(max_length=1000)
    isActive = models.BooleanField(db_column='isActive')

    def name (self):
        return self.isParam.name

    class Meta:
        db_table = "is_param_class"

class ClassSCISMap (models.Model):
    ismap = models.ForeignKey(SCISMap, db_column="sc_is_map_id", verbose_name="Strategy Component: Intervention Selector")
    theClass = models.ForeignKey(Class, db_column="classId", verbose_name="Class")
    isActive = models.BooleanField()

    class Meta:
        db_table = "class_sc_is_map"

# Some Base ISParams have legal values.  This is a record of a legal value for a param.
class ISParamValue (models.Model):
    isParam = models.ForeignKey(ISParamBase, db_column="isparamid",verbose_name="Base IS Param")
    value = models.CharField(max_length=500)

    class Meta:
        db_table = "is_param_value"

    def __str__ (self):
        intsel = self.isParam.interventionSelector
        return intsel.name + ": " + self.isParam.name + "=" + self.value


class Part (models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = "part"

    def __str__ (self):
        return self.name

class Machine (models.Model):
    name = models.CharField(max_length=45)
    parts = models.ManyToManyField(Part, through='Machine2Part')
    class Meta:
        db_table = "machine"

    def __str__ (self):
        return self.name


class Machine2Part (models.Model):
    machine = models.ForeignKey(Machine,db_column='machineId')
    part = models.ForeignKey(Part,db_column='partId')
    class Meta:
        db_table = "machine2part"








