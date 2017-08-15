from msadmin.models import *
from django.db import transaction
#When a strategy is added to a class we use the following two functions to copy data from tables
# that define defaults into class-specific tables.


def createCustomStrategyForClass (aclass, strategyName, loginSC, lessonSC, tutorSC, lc, descr):
    with transaction.atomic():
        clstrat = Strategy_Class(theClass=aclass,strategy=None,lc=lc,name=strategyName, description=descr)
        clstrat.save()
        copyStrategyComponentToClass(aclass,loginSC,clstrat)
        copyStrategyComponentToClass(aclass,lessonSC,clstrat)
        copyStrategyComponentToClass(aclass,tutorSC,clstrat)

# Copy the 3 strategy-components of a strategy to a class.
# WHen this successfully completes there will be rows add to the following tables:
# class_sc_is_map :  on/off switch for each intervention selector
# class_is_param:  a parameter for each intervention selector (a copy of the is_param)
# class_sc_param: a parameter for each strat-component (a copy of sc_param)
def copyStrategyToClass (aclass,strategy):
    # defines an atomic db transaction that will only be commited if all the operations within this block are successful.
    with transaction.atomic():
        clstrat = Strategy_Class(theClass=aclass,strategy=strategy,lc=strategy.lc,name=strategy.name, description=strategy.description)
        clstrat.save()
        copyStrategyComponentToClass(aclass,strategy.lesson,clstrat)
        copyStrategyComponentToClass(aclass,strategy.login,clstrat)
        copyStrategyComponentToClass(aclass,strategy.tutor,clstrat)

# Copy a strategy components params and intervention selector info to a class
def copyStrategyComponentToClass (aclass, strategyComponent, classStrategy):
    scCl = SC_Class(theClass=aclass,sc=strategyComponent,classStrategy=classStrategy)
    scCl.save()
    copyStrategyComponentParamsToClass(aclass,strategyComponent,scCl)
    copyStrategyComponentInterventionSelectorsToClass(aclass,strategyComponent,scCl)

# for every scis_map row, create a class_sc_is_map row.
# This is just a row for each intervention selector that is setting it to ON and
# it has a copy of the IS config from the scismap
def createSCISMaps (aclass, strategyComponent,classSC):
    scisMaps = SCISMap.objects.filter(strategyComponent=strategyComponent)
    for m in scisMaps:
        cm = ClassSCISMap(ismap=m, config=m.config,theClass=aclass,isActive=True,classSC=classSC)
        cm.save()

# Copy the intervention selectors of a strategy component into a class.  This involves
# creating a row in Class_sc_is_map for each interv-selector that turns on the interv-selector.
# It also means creating a class_is_param for each is-param-sc.
# After the is-params-sc rows have been copied to is-param-class rows we need to create additional rows in the is-param-class table
# for each is-param-base that is not mentioned in the is-param-sc.   Those params will be copied in as INACTIVE.
#  The reason this is done is so that the intervention selector will have these params in the list so that the author can turn them on if desired.
def copyStrategyComponentInterventionSelectorsToClass(aclass, strategyComponent, classSC):

    # Get the intervention selectors for the strategy component
    interventionSelectors = strategyComponent.interventionSelectors.all()
    # copy all their scis parameters into the class_is_params
    for intsel in interventionSelectors:
        # for bp in intsel.getBaseParams():
        scisParams = intsel.getParams(strategyComponent)
        for bp in scisParams:
            # copyBaseParamToClass(aclass,bp)
            copySCISParamToClass(aclass,bp, classSC)
        # Now we copy in the is-param-base objects that are not within this sc-is and make them inactive
        copyUnusedSCISParamsToClass(aclass,intsel,scisParams,classSC)
        # Now we use the strategy component's is params to overwrite the values that came from base is params
        # overwriteParams(aclass,strategyComponent, intsel)
    # Now set all the intervention selectors in this sc as active
    createSCISMaps(aclass,strategyComponent,classSC)

# Params have been copied from the base is_params to the class is_params.
#  THis will go through the is_params based on the strategy component and
# overwrite what is in the class is param with those values.  It will also set the
# param to active=true
def overwriteParams (aclass, strategyComponent, intsel):
    sc_isParams = intsel.getParams(strategyComponent)
    # go through the is-params that are part of this intervention within this strategy component
    for p in sc_isParams:
        # From the sc_is_param get the corresponding class_is_param
        c_isParam = ClassISParam.objects.get(theClass=aclass, isParam=p.baseParam)
        c_isParam.isActive = p.isActive
        c_isParam.value = p.value
        c_isParam.save()


# This creates is-param-class objects that are inactive for each is-param-base object that is NOT AMONG
# parameters assigned in the list of is-param-sc  objects.
def copyUnusedSCISParamsToClass (aclass, intsel,scisParams, classSC):
    baseParams = intsel.getBaseParams()
    for bp in baseParams:
        found = False
        #see if the base param is among the scisParams
        for p in scisParams:
            if p.baseParam == bp:
                found = True
                break
        # When its not found, we want to create an is-param-class object for it that is inactive.
        # Possible problem:  We are wanting to create a is param-class from a is-param-base but there is no is-param-sc for this and the is-param-class
        # has a foreign key to an is-param-sc.  THis FK allows NULL
        if not found:
            copyBaseParamToClass(aclass,bp, classSC)


# Copy the base is param to the class is param and make it inactive.
def copyBaseParamToClass (aclass, baseParam, classSC):
    cp = ClassISParam(theClass=aclass, classSC=classSC, scisParam=None, isParam=baseParam, name=baseParam.name, value=baseParam.value, isActive=False)
    cp.save()

# Copy the scis param to the class is param and make it inactive.
def copySCISParamToClass (aclass, scisParam, classSC):
    cp = ClassISParam(theClass=aclass, classSC=classSC, scisParam=scisParam, isParam=scisParam.baseParam, name=scisParam.name, value=scisParam.value, isActive=scisParam.isActive)
    cp.save()


# Copy the intervention selectors params from is_param to class_is_param
# def copyInterventionSelectorToClass(aclass, strategyComponent, intsel):
#     # Gets the params for the intervention selector based on the strategy component.   Goes to the is_param table.
#     params = intsel.getParams(strategyComponent)
#     for p in params:
#         # create a new class_is_param and set its value to be what is in the is_param
#         cp = ClassISParam(theClass=aclass, isParam=p, value=p.value)
#         cp.save()


# For each SC param make a class_SC_param and copy its value.
def copyStrategyComponentParamsToClass (aclass, strategyComponent, classSC):
    scParams = strategyComponent.params.all() # gets a list of StrategyComponentParam objects
    for p in scParams:
        cp = ClassSCParam(scParam=p,theClass=aclass,classSC=classSC,name=p.name,value=p.value,isActive=True)
        cp.save()

# When a strategy is removed from a class we delete the specific settings of intervention selector params
# and strategy component params

# Remove the classes strategy components params
def removeStrategyComponentParamsFromClass(aclass, strategyComponent, classSC):
    scParams = strategyComponent.params.all() # gets a list of StrategyComponentParam objects
    for p in scParams:
        cparams = ClassSCParam.objects.filter(scParam=p,theClass=aclass,classSC=classSC)
        for cp in cparams:
            cp.delete()



# Get rid of all class_sc_is_map rows for this class and strategy-comp
def removeSCISMapsFromClass (aclass, strategyComponent) :
    scisMaps = SCISMap.objects.filter(strategyComponent=strategyComponent)
    for m in scisMaps:
        cmaps = ClassSCISMap.objects.filter(ismap=m,theClass=aclass)
        for cm in cmaps:
            cm.delete()


# remove the interv-sel params
def removeInterventionSelectorParamsFromClass(aclass, intsel, classSC):
    # use all the base params for an intsel to locate the class isParams.  Delete them.
     params = intsel.getBaseParams()
     for p in params:
         iparams = ClassISParam.objects.filter(theClass=aclass, isParam=p, classSC=classSC)
         for cp in iparams:
            cp.delete()

# remove the switches that turn on intervention selectors (class_sc_is_map)
# and the interv-sel params
def removeStrategyComponentInterventionSelectorsFromClass(aclass, strategyComponent, classSC):
    removeSCISMapsFromClass(aclass,strategyComponent)
    for intsel in strategyComponent.interventionSelectors.all():
        removeInterventionSelectorParamsFromClass(aclass,intsel, classSC)



# remove the components params and intervention selector info
def removeStrategyComponentFromClass(aclass, strategyComponent, classStrategy):
    classSC = SC_Class.objects.get(theClass=aclass,sc=strategyComponent,classStrategy=classStrategy)
    removeStrategyComponentParamsFromClass(aclass,strategyComponent,classSC)
    removeStrategyComponentInterventionSelectorsFromClass(aclass,strategyComponent,classSC)
    classSC.delete()


# remove the info about all three components
# Foreign-key on-delete=cascade exists on sc_class -> strategy_class so deleting the strategy_class will cause the sc_class rows to get deleted
# FK class_sc_param -> sc_class on-delete=cascade so deleting the sc_class causes the class_sc_params to get deleted
# FK is_param_class -> sc_class on-delete=cascade so deleting the sc_class causes the is_param_class rows to get deleted.
# FK class_sc_is_map -> sc_class on-delete=cascade so deleting the sc_class causes the class_sc_is_map rows to get deleted.
def removeStrategyFromClass (aclass,strategyClass):
    # removeStrategyComponentFromClass(aclass, strategy.lesson, classStrategy)
    # removeStrategyComponentFromClass(aclass, strategy.login, classStrategy)
    # removeStrategyComponentFromClass(aclass, strategy.tutor, classStrategy)
    strategyClass.delete()




