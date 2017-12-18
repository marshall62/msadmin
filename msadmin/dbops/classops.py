from django.db import transaction

from msadmin.stratauth.models import *


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
        scismap = SCISMap.objects.filter(interventionSelector=intsel, strategyComponent=strategyComponent)
        scisParams = InterventionSelectorParam.objects.filter(scismap=scismap)
        # for bp in intsel.getBaseParams():
        # scisParams = intsel.getParams(strategyComponent)
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


# clones the structure of a strategy in some other class into this class.   This means copying all the
# class-level rows from one to the other.   It can't copy generic versions of objects (such as in above functions)
def copyStrategyFromOtherClass (thisClass, otherClass, classStrategy):
    with transaction.atomic():
        # Clone the Strategy_Class object
        if classStrategy.strategy_id == None:
            classStrategy.strategy = None
        strat = Strategy_Class(strategy=classStrategy.strategy, theClass=thisClass, lc=classStrategy.lc, name=classStrategy.name, description=classStrategy.description)
        strat.save()
        # get the three (class) strategy components
        scs= SC_Class.objects.filter(theClass=otherClass, classStrategy=classStrategy)
        # clone each of the (class) SC objects.
        for sc in scs:
            # clone the SC
            new_sc = SC_Class(theClass=thisClass, sc=sc.sc, classStrategy=strat)
            new_sc.save()

            # Clone the SC's params
            # get all the sc params from this sc
            sc_params = ClassSCParam.objects.filter(classSC=sc)
            # clone all of them
            for p in sc_params:
                new_p = ClassSCParam(scParam=p.scParam,theClass=thisClass,classSC=new_sc,isActive=p.isActive,name=p.name,value=p.value)
                new_p.save()


            # get the (class) scismaps connected to this SC and clone
            scismaps= ClassSCISMap.objects.filter(classSC=sc)
            for scismap in scismaps:
                # clone the map
                new_scismap = ClassSCISMap(ismap=scismap.ismap,theClass=thisClass,isActive=scismap.isActive,config=scismap.config,classSC=new_sc)
                new_scismap.save()
            # get all the intervention selector params associated with this SC and clone them
            isparams = ClassISParam.objects.filter(classSC=sc)
            for isp in isparams:
                new_isp = ClassISParam(isParam=isp.isParam,scisParam=isp.scisParam,theClass=thisClass,classSC=new_sc,name=isp.name,value=isp.value,isActive=isp.isActive)
                new_isp.save()
        return strat


    # Clone its sub-structure objects



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

def indent (n):
    return "&nbsp;" * n


# This is only a testing routine not associated with anything in the website.   I will call it directly
# Its purpose is to validate the generic structures that define tutoring strategies.   These are complicated
# and it is possible through user error to omit necessary things which can result in structures that are incorrect

# This validator helps make sure that all SCISMaps have the correct number of is-param-sc rows
#  Each IS has a number of is-param-base rows which define all the possible params for the selector
#  Each SCISMap should set up an is-param-sc that goes with the is-param-base.  So the number of params should be the same.
#  Almost all of them should be isActive=true to indicate that the param is in use.  A small number may be turned off and they will be reported on here.

def validateSCISMaps_have_necessary_is_param_sc ():
    maps = SCISMap.objects.all()
    strbuf = ""
    for m in maps:
        sc = m.strategyComponent
        insel = m.interventionSelector
        is_param_bases = insel.getBaseParams()
        n_base_isparams = is_param_bases.__len__()
        is_param_scs = m.getISParams()
        n_sc_isparams = is_param_scs.__len__()
        if (n_base_isparams != n_sc_isparams):
            strbuf += "Failure: sc_is_map (" + str(m.pk) + ") for strategy_component (" + str(sc.pk) + ") " + sc.name + "\n<br>"
            strbuf += "&nbsp; &nbsp; intervention_selector (" + str(insel.pk) + ") " + insel.name + " has " + str(n_base_isparams) + ":<br>"
            for bp in is_param_bases:
                strbuf += "&nbsp; &nbsp; &nbsp; &nbsp; (" + str(bp.pk) + ") " + bp.name + "="+ bp.value + "\n<br>"
            strbuf += "&nbsp; &nbsp; But the sc_is_map sets " + str(n_sc_isparams) + " of them:<br>"
            for p2 in is_param_scs:
                strbuf += "&nbsp; &nbsp; &nbsp; &nbsp; (" + str(p2.pk) + ") " + p2.name + "=" + p2.value + "\n<br>"

            # strbuf += "&nbsp;&nbsp;"+ sc.name + " : " + insel.name + "\n<br>"
            # print("Failure: scismap id:", m.pk)
            # print("    ", sc.name, ":", insel.name)
            # print("Failure:  SCISmap id: " + m.pk + " has IS " + insel.name + " with " , n_base_isparams , " base params but " , n_sc_isparams , " sc-is-params.  Number should be same")
        for p in is_param_scs:
            if not p.isActive:
                # print("In ", sc.name, ":", insel.name, " the param", p.name, "is inactive")
                strbuf += "Warning: is_param_sc (" + str(p.pk) + ") " + sc.name + " : " + insel.name + "-- The param " + p.name + " is inactive" + "\n<br>"
        # strbuf += "<br>"
    return strbuf

def validate_scismaps (sc, il):
    strbuf = ""
    scismaps = SCISMap.objects.filter(strategyComponent=sc)
    for m in scismaps:
        insel = m.interventionSelector
        is_param_bases = insel.getBaseParams()
        n_base_isparams = is_param_bases.__len__()
        is_param_scs = m.getISParams()
        n_sc_isparams = is_param_scs.__len__()
        if (n_base_isparams != n_sc_isparams):
            strbuf += indent(il) + "Failure: sc_is_map (" + str(m.pk) + ") for strategy_component (" + str(sc.pk) + ") " + sc.name + "\n<br>"
            strbuf += indent(il+4) +"Intervention_selector (" + str(insel.pk) + ") " + insel.name + " has " + str(n_base_isparams) + ":<br>"
            for bp in is_param_bases:
                strbuf += indent(il+4) +" &nbsp; &nbsp; (" + str(bp.pk) + ") " + bp.name + "="+ bp.value + "\n<br>"
            strbuf += indent(il+4) +"But the sc_is_map sets " + str(n_sc_isparams) + " of them:<br>"
            for p2 in is_param_scs:
                strbuf += indent(il+4) +"(" + str(p2.pk) + ") " + p2.name + "=" + p2.value + "\n<br>"

                # strbuf += "&nbsp;&nbsp;"+ sc.name + " : " + insel.name + "\n<br>"
                # print("Failure: scismap id:", m.pk)
                # print("    ", sc.name, ":", insel.name)
                # print("Failure:  SCISmap id: " + m.pk + " has IS " + insel.name + " with " , n_base_isparams , " base params but " , n_sc_isparams , " sc-is-params.  Number should be same")
        for p in is_param_scs:
            if not p.isActive:
                # print("In ", sc.name, ":", insel.name, " the param", p.name, "is inactive")
                strbuf += indent(il) +"Warning: is_param_sc (" + str(p.pk) + ") " + sc.name + " : " + insel.name + "-- The param " + p.name + " is inactive" + "\n<br>"
    return strbuf

def validate_strategy_scismaps (strat, il):
    sc_login = strat.login
    sc_lesson = strat.lesson
    sc_tutor = strat.tutor
    msg = ""
    msg += validate_scismaps (sc_login,il)
    msg += validate_scismaps (sc_lesson,il)
    msg += validate_scismaps (sc_tutor,il)
    return msg



# Make sure the sc has only the expected params and that they are all present
def validate_sc_2 (sc, expected_params, il):
    maps = SCParamMap.objects.filter(strategyComponent=sc)
    strbuf = indent(il) + "Validating SC (" + str(sc.pk) + ") " + sc.name + "<br>"
    found_params = []
    for m in maps:
        p = m.param
        found_params.append(p.name)
        if not p.name in expected_params:
            strbuf += indent(il+4) + "Warning: sc-param (" + str(p.pk) + ") " + p.name + " found. This is not appropriate for this sc\n<br>"
    for ep in expected_params:
        if not ep in found_params:
            strbuf += indent(il+4) + "Failure: sc_param " + ep + " is not found among the params for this sc\n<br>"
    return strbuf


#  It is possible that a strategy component does not have the correct number of parameters so that it can run correctly.
# THere is nothing in the db to indicate which parameters must be set for each SC so the knowledge is coded in here.
def validate_sc_params (strat, il):

    sc = strat.lesson
    strbuf = ""
    lesson_params = [ 'maxTimeInTopicSecs', 'contentFailureThreshold', 'topicMastery', 'minNumberProbs', 'maxNumberProbs', 'minTimeInTopicSecs']
    strbuf += validate_sc_2(sc,lesson_params,il)

    sc = strat.tutor
    tutor_params = [ 'studentModelClass', 'problemSelectorClass', 'reviewModeProblemSelectorClass', 'challengeModeProblemSelectorClass', 'problemReuseIntervalSessions', 'problemReuseIntervalDays', 'displayMyProgressPage', 'hintSelectorClass','difficultyRate']
    strbuf += validate_sc_2(sc,tutor_params,il)

    return strbuf

def validateStrategy (strat):
    msg = "Validating strategy (" + str(strat.pk) + ") " + strat.name + "<br>"
    msg += validate_sc_params(strat,4)
    msg += '--<br>'
    msg += validate_strategy_scismaps(strat,4)
    msg += '-----------------------------------------------------<br><br>'
    return msg

def validate_all_strategies () :
    strats = Strategy.objects.all()
    strbuf = ""
    for s in strats:
        strbuf += validateStrategy(s)
    return strbuf

def validateGenericStructure ():
    strats = Strategy.objects.all()
    messages =  ""
    for strat in strats:
        messages += validateStrategy(strat)
    return messages

def validateClassTutoringStrategies (request):
    pass