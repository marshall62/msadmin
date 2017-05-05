from django.db import models


# Create your models here.


class InterventionSelector(models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    onEvent = models.CharField(max_length=45)
    className = models.CharField(max_length=100)

    # uses the wayangoutpostdb.intervention_selector table
    class Meta:
        db_table = "intervention_selector"

    def publish (self):
        self.save()

    def __str__(self):
        return self.name

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
    # supports the many-to-many relationship from StrategyComponent to StrategyComponentParam via the sc_is_map
    params = models.ManyToManyField(StrategyComponentParam, through='SCParamMap')
    #id = models.IntegerField(primary_key=True);

    class Meta:
        db_table = "strategy_component"

    def publish (self):
        self.save()

    def __str__(self):
        return self.name


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

    class Meta:
        db_table = "sc_is_map"



    def __str__(self):
        return self.strategyComponent.__str__() + ":" + self.interventionSelector.__str__()


class InterventionSelectorParam(models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    value = models.CharField(max_length=500)
    interventionSelector = models.ForeignKey(SCISMap, db_column="sc_is_map_id",verbose_name="StrategyComponent:InterventionSelector")

    class Meta:
        db_table = "is_param"

    # TODO would like to be able to have a name like CollabLogin.Pretest: runFreq = oncePerSession  (maybe first 20 chars of the value)
    # This would require some kind of query thru the SCISMap FK to get the strategy component and the intervention selector
    def __str__(self):
        #m = SCISMap.objects.get(interventionSelector=self.id)
        return self.name

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
    isParam = models.ForeignKey(InterventionSelectorParam, db_column="is_param_id",verbose_name="Intervention Selector Param")
    theClass = models.ForeignKey(Class, db_column="classId", verbose_name="Class")
    value = models.CharField(max_length=500)

    class Meta:
        db_table = "class_is_param"

class ClassSCISMap (models.Model):
    ismap = models.ForeignKey(SCISMap, db_column="sc_is_map_id", verbose_name="Strategy Component: Intervention Selector")
    theClass = models.ForeignKey(Class, db_column="classId", verbose_name="Class")
    isActive = models.BooleanField()

    class Meta:
        db_table = "class_sc_is_map"



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

    def __str__ (self):
        m = Machine.objects.get(pk=self.machine)
        p = Part.objects.get(pk=self.part)
        return m.name + ":" + p.name







