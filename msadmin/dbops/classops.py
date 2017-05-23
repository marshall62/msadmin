from msadmin.models import *
#When a strategy is added to a class we use the following two functions to copy data from tables
# that define defaults into class-specific tables.


# Copy the 3 strategy-components of a strategy to a class.
# WHen this successfully completes there will be rows add to the following tables:
# class_sc_is_map :  on/off switch for each intervention selector
# class_is_param:  a parameter for each intervention selector (a copy of the is_param)
# class_sc_param: a parameter for each strat-component (a copy of sc_param)
def copyStrategyToClass (aclass,strategy):
    copyStrategyComponentToClass(aclass,strategy.lesson)
    copyStrategyComponentToClass(aclass,strategy.login)
    copyStrategyComponentToClass(aclass,strategy.tutor)

# Copy a strategy components params and intervention selector info to a class
def copyStrategyComponentToClass (aclass, strategyComponent):
    copyStrategyComponentParamsToClass(aclass,strategyComponent)
    copyStrategyComponentInterventionSelectorsToClass(aclass,strategyComponent)

# for every scis_map row, create a class_sc_is_map row.
# This is just a row for each intervention selector that is setting it to ON
def createSCISMaps (aclass, strategyComponent):
    scisMaps = SCISMap.objects.filter(strategyComponent=strategyComponent)
    for m in scisMaps:
        cm = ClassSCISMap(ismap=m, theClass=aclass,isActive=True)
        cm.save()

# Copy the intervention selectors of a strategy component into a class.  This involves
# creating a row in Class_sc_is_map for each interv-selector that turns on the interv-selector.
# It also means creating a class_is_param for each interv_selector's param
def copyStrategyComponentInterventionSelectorsToClass(aclass, strategyComponent):

    # Get the intervention selectors for the strategy component
    interventionSelectors = strategyComponent.getInterventionSelectors()
    # copy all their base parameters into the class_is_params
    for intsel in interventionSelectors:
        for bp in intsel.getBaseParams():
            copyBaseParamToClass(aclass,bp)
        # Now we use the strategy component's is params to overwrite the values that came from base is params
        overwriteParams(aclass,strategyComponent, intsel)
    # Now set all the intervention selectors in this sc as active
    createSCISMaps(aclass,strategyComponent)

# Params have been copied from the base is_params to the class is_params.
#  THis will go through the is_params based on the strategy compeonent and
# overwrite what is in the class is param with those values.  It will also set the
# param to active=true
def overwriteParams (aclass, strategyComponent, intsel):
    sc_isParams = intsel.getParams(strategyComponent)
    # go through the is params that are part of this intervention within this strategy component
    # and set the corresponding class is param to have isActive=true
    for p in sc_isParams:
        # From the sc_is_param get the corresponding class_is_param
        c_isParam = ClassISParam.objects.get(theClass=aclass, isParam=p.baseParam)
        c_isParam.isActive = True
        c_isParam.value = p.value
        c_isParam.save()

# Copy the base is param to the class is param and make it inactive.
def copyBaseParamToClass (aclass, baseParam):
    cp = ClassISParam(theClass=aclass, isParam=baseParam, value=baseParam.value, isActive=False)
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
def copyStrategyComponentParamsToClass (aclass, strategyComponent):
    scParams = strategyComponent.getParams() # gets a list of StrategyComponentParam objects
    for p in scParams:
        cp = ClassSCParam(scParam=p,theClass=aclass,value=p.value)
        cp.save()

# When a strategy is removed from a class we delete the specific settings of intervention selector params
# and strategy component params

# Remove the classes strategy components params
def removeStrategyComponentParamsFromClass(aclass, strategyComponent):
    scParams = strategyComponent.getParams() # gets a list of StrategyComponentParam objects
    for p in scParams:
        cparams = ClassSCParam.objects.filter(scParam=p,theClass=aclass)
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
def removeInterventionSelectorParamsFromClass(aclass, intsel, strategyComponent):
    # use all the base params for an intsel to locate the class isParams.  Delete them.
     params = intsel.getBaseParams()
     for p in params:
         iparams = ClassISParam.objects.filter(theClass=aclass, isParam=p)
         for cp in iparams:
            cp.delete()

# remove the switches that turn on intervention selectors (class_sc_is_map)
# and the interv-sel params
def removeStrategyComponentInterventionSelectorsFromClass(aclass, strategyComponent):
    removeSCISMapsFromClass(aclass,strategyComponent)
    for intsel in strategyComponent.getInterventionSelectors():
        removeInterventionSelectorParamsFromClass(aclass,intsel,strategyComponent)


# remove the components params and intervention selector info
def removeStrategyComponentFromClass(aclass, strategyComponent):
    removeStrategyComponentParamsFromClass(aclass,strategyComponent)
    removeStrategyComponentInterventionSelectorsFromClass(aclass,strategyComponent)


# remove the info about all three components
def removeStrategyFromClass (aclass,strategy):
    removeStrategyComponentFromClass(aclass,strategy.lesson)
    removeStrategyComponentFromClass(aclass,strategy.login)
    removeStrategyComponentFromClass(aclass,strategy.tutor)




