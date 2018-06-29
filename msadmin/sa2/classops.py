from django.db import transaction
from django.shortcuts import get_object_or_404

from msadmin.sa2.models import *


#When a strategy is added to a class we use the following two functions to copy data from tables
# that define defaults into class-specific tables.
def createCustomStrategyForClass (aclass, strategyName, loginSC, lessonSC, tutorSC, lc, descr):
    with transaction.atomic():
        actstrat = Strategy(name=strategyName,lc=lc, description=descr, aclass=aclass)
        actstrat.save()
        makeActualStrategyComponent(aclass, loginSC, actstrat)
        makeActualStrategyComponent(aclass, lessonSC, actstrat)
        makeActualStrategyComponent(aclass, tutorSC, actstrat)

# Makes the generic SC and its substructure from an actual SC
def makeGenericSCFromActual (asc):
    gsc = StrategyComponent(name=asc.name,description=asc.description, briefDescr=asc.briefDescr, className=asc.className, type=asc.type, is_generic=True)
    gsc.save()
    # create the SCISMaps
    makeGenericSCISMapsFromActual(asc,gsc)
    # make the SC Params
    paramMaps = SCParamMap.objects.filter(strategyComponent=asc)
    for m in paramMaps:
        scp = makeGenericSCParamFromActual(m.param)
        # When creating a generic SC param map we set its isActive based on the actual's param.isActive
        gm = SCParamMap(strategyComponent=gsc,param=scp,is_active=m.param.isActive)
        gm.save()
    return gsc


def makeGenericSCParamFromActual (ascParam):
    p = StrategyComponentParam(name=ascParam.name, value=ascParam.value, description=ascParam.description, isActive=ascParam.isActive)
    p.save()
    return p


# Making the generic SCISMaps from an actual means making SCISMaps that are similar
# but they link the generic SC to the generic parent IS.
def makeGenericSCISMapsFromActual (asc, gsc):
    maps = SCISMap.objects.filter(strategyComponent=asc)
    # make the a similar SCISMap but link to the generic parent of the actual IS
    for m in maps:
        gm = SCISMap(strategyComponent=gsc,interventionSelector=m.interventionSelector.genericParent, isActive=m.isActive, config=m.config)
        gm.save()
        # Now take the ISParams from the actual SCISMap and make generic versions
        aISParams = m.getISParams()
        for ap in aISParams:
            gp = InterventionSelectorParam(name=ap.name,value=ap.value,isActive=ap.isActive,baseParam=ap.baseParam,scismap=gm)
            gp.save()

def makeUniqueName (rootName, suffix):
    i = 1
    # Give it a unique name with -Generic-N
    while True:
        name = rootName + "-" +suffix+"-" + str(i)
        other = Strategy.objects.filter(name=name)
        if other.count() == 0:
            return name
        i += 1

#  This will take an actual strategy used by a class and make a generic version of it so that anyone can easily use it.
#  Nothing special needs to be done.  Just make a clone of the full structure and make sure everything has myStrategy=None
def makeGenericStrategyFromActual (stratId):
    astrat = get_object_or_404(Strategy, pk=stratId)

    gstrat = Strategy(description=astrat.description, lc=astrat.lc)
    gstrat.name = makeUniqueName(astrat.name, "Generic")
    gstrat.save()
    gstrat.login = makeGenericSCFromActual(astrat.login)
    gstrat.lesson = makeGenericSCFromActual(astrat.lesson)
    gstrat.tutor = makeGenericSCFromActual(astrat.tutor)
    gstrat.save()
    return gstrat


# Copy the 3 strategy-components of a strategy to a class.
# WHen this successfully completes there will be rows add to the following tables:
# class_sc_is_map :  on/off switch for each intervention selector
# class_is_param:  a parameter for each intervention selector (a copy of the is_param)
# class_sc_param: a parameter for each strat-component (a copy of sc_param)
def makeActualStrategyFromGeneric (aclass, strategy):
    # defines an atomic db transaction that will only be commited if all the operations within this block are successful.
    with transaction.atomic():
        actstrat = Strategy.getActual(strategy,aclass)
        actstrat.name = makeUniqueName(strategy.name, "Actual")
        actstrat.save()
        actLessonSC = makeActualStrategyComponent(actstrat, strategy.lesson)
        actLoginSC = makeActualStrategyComponent(actstrat, strategy.login)
        actTutorSC = makeActualStrategyComponent(actstrat, strategy.tutor)
        actstrat.lesson = actLessonSC
        actstrat.tutor = actTutorSC
        actstrat.login = actLoginSC
        actstrat.save()
        return actstrat


# Copy a generic strategy component into the actual strategy as an actual SC
# The generic strategy component is linked to the intervention selectors it uses through the SCISMap (which also has an isActive flag
# that can be used to turn off an IS within an SC).  Other ISs with a type equal to the type of the SC should be added to the
# new actual SC and set to inactive.  This way an author can modify the strategy by activating intervention selectors that were
# inactive or not present in the generic SC
def makeActualStrategyComponent (actualStrategy, gstrategyComponent):
    actsc = StrategyComponent.getActual(gstrategyComponent)
    actsc.strategy = actualStrategy
    actsc.save()
    # The actual SC now needs its parameters to be copied from the generic
    makeActualSCParams(actsc,gstrategyComponent,actualStrategy)
    # The actual SC now needs its intervention selectors to be copied from the generic
    # and augmented with inactive versions of those that are not part of the generic SC
    makeActualInterventionSelectors(actsc,gstrategyComponent,actualStrategy)
    return actsc


# When an active SC is made from a generic SC we copy all the SCISMap links between the generic SC and its ISs.
# There are possibly remaining ISs that were not linked from the generic SC.  These ISs must have the same type as the generic SC.
#  We then make SCISMap links to these and set them to inactive.  The result is a new active SC that has all the intervention
# selectors appropriate to that type of SC but only those ISs that were active in the generic are active in the actual.
def makeActualInterventionSelectors(asc, gsc, actualStrat):

    # Get the generic intervention selectors for the strategy component
    interventionSelectors = gsc.interventionSelectors.all()
    # copy all their scis parameters into the class_is_params
    for gIS in interventionSelectors:
        scismap = SCISMap.objects.filter(interventionSelector=gIS, strategyComponent=gsc).first()
        actualIS = InterventionSelector.getActual(gIS,actualStrat)
        actualIS.save()
        # Make actual SCIS map
        ascismap = SCISMap(interventionSelector=actualIS,strategyComponent=asc)
        ascismap.myStrategy = actualStrat
        # The config for the IS is on the generic scismap and should be cloned to the actual
        ascismap.config = scismap.config
        ascismap.isActive = scismap.isActive
        ascismap.save()

        # Set up the actual IS with all its params (both active and inactive following a similar method to the way we add ISs to SCs)

        # First take the params that are connected to the generic IS and make actuals from them. These may be active or inactive.
        setActualISParams(actualIS,ascismap,gIS,gsc,actualStrat)
        # We now want to get base parameters from the IS itself.  We want only those that were obtained from the generic IS.
        # These are set up as inactive params in the actual IS.
        addInactiveISParamsFromISBaseParams(gsc, asc, gIS, actualIS, actualStrat)

    # Now there may be intervention selectors that are not connected to the GSC and we want them to be
    # added to the strategy component as inactive.   Get the ones with a type that matches the GSC
    otherISs = InterventionSelector.objects.filter(type=gsc.type, myStrategy=None)
    others = set(otherISs)
    used = set(interventionSelectors)
    unused = others.difference(used)

    # Make actual ISs and SCISmaps to the actual SC for the other unused intervention selectors
    for guIS in unused:
        auIS = InterventionSelector.getActual(guIS,actualStrat)
        auIS.save()
        m = SCISMap(interventionSelector=auIS,strategyComponent=asc,myStrategy=actualStrat,isActive=False)
        m.save()
        # add in all the base IS params to the new actual IS and make them inactive.
        addInactiveISParamsFromISBaseParams(gsc, asc, guIS, auIS, actualStrat)



def setActualISParams (actIS, ascismap, gIS, gSC, actualStrat):
    # A guess for now.  Lifted from above.  TODO.  Make it do what the name says
    # scisParams = InterventionSelectorParam.objects.filter(scismap=scismap)
    # Get the params from the generic IS and make actual versions of them to put in the actual IS
    g_is_params = gIS.getParams(gSC)
    # for bp in intsel.getBaseParams():
    # scisParams = intsel.getParams(strategyComponent)
    for g_isp in g_is_params:
        a_isp = InterventionSelectorParam.getInstanceFromGenericParam(g_isp,actualStrat)
        a_isp.scismap =  ascismap
        # a_isp.interventionSelector = actIS
        a_isp.save()



# We now want to get base parameters from the IS itself.  We want only those that were obtained from the generic IS.
# These are set up as inactive params in the actual IS.

def addInactiveISParamsFromISBaseParams (genericSC, actualSC, genericIS, actualIS, actualStrat):
    # The actual IS has been given the params from the generic IS.  It should also be given params that were not in the generic.
    # THese come from the base params of the generic IS. The base params are all the *possible* params (which may have been grown)
    # since the time the generic strategy was built and we'd like them to be available to an author for adding in if they wish.

    scismap = SCISMap.objects.get(interventionSelector=actualIS, strategyComponent=actualSC)
    # Get the base params that are not among the params of the generic IS
    baseParams = genericIS.getInactiveParams(genericSC)
    # Create inactive params from these base params and add them to the actual IS
    #  This allows authors to turn them on if they want.
    for bp in baseParams:
        ap = InterventionSelectorParam.getInstanceFromBaseParam(bp,actualStrat)
        ap.scismap = scismap
        ap.interventionSelector = actualIS
        ap.save()
        # The intervention selector doesn't hold its params in any field.  When we need them, they are queried.





# Copy the intervention selectors params from is_param to class_is_param
# def copyInterventionSelectorToClass(aclass, strategyComponent, intsel):
#     # Gets the params for the intervention selector based on the strategy component.   Goes to the is_param table.
#     params = intsel.getParams(strategyComponent)
#     for p in params:
#         # create a new class_is_param and set its value to be what is in the is_param
#         cp = ClassISParam(theClass=aclass, isParam=p, value=p.value)
#         cp.save()


# Given the generic SC and the actual SC,
# make actual SC params from each of the generic SC params and add these to the actual SC
# Returns the list of params so that the caller can add them into their SC
# def makeActualSCParams (asc, gsc, astrat):
#     gscparams = gsc.params.all() # gets a list of StrategyComponentParam objects
#     for gp in gscparams:
#         ap = StrategyComponentParam.getActual(gp,astrat)
#         ap.save()
#         m = SCParamMap(strategyComponent=asc,param=ap,myStrategy=astrat)
#         m.save()
#     asc.save()

def makeActualSCParams (asc, gsc, astrat):
    gscparam_maps = SCParamMap.objects.filter(strategyComponent=gsc)
    for m in gscparam_maps:
        gp = m.param
        ap = StrategyComponentParam.getActual(gp,astrat)
        # When copying the generic we use the isActive value on the map to determine if the param isActive by default or not.
        ap.isActive = m.is_active
        ap.save()
        m = SCParamMap(strategyComponent=asc,param=ap,myStrategy=astrat)
        m.save()
    asc.save()




# clones the structure of a strategy in an other class into this class.   This means copying the whole deep structure
# that represents the strategy.
def copyStrategyFromOtherClass (thisClass, classStrategy):
    with transaction.atomic():
        # Clone the Strategy object
        new_strat = Strategy.getActual(classStrategy, thisClass) # the constructor can be used with either an actual or a generic
        new_strat.save()
        # get the three strategy components
        scs=  [classStrategy.login, classStrategy.lesson, classStrategy.tutor]
        new_scs = []
        # clone each of the SC objects.
        for sc in scs:
            # clone the SC
            new_sc = StrategyComponent.getActual(sc)
            new_scs.append(new_sc)
            new_sc.save()

            # get all the sc params from this sc
            # clone all of them and connect to the new SC
            for p in sc.getParams():
                new_p = StrategyComponentParam.getActual(p,new_strat)
                new_p.save()
                new_m = SCParamMap(strategyComponent=new_sc, param=new_p)
                new_m.myStrategy = new_strat
                new_m.save()


            # get the scismaps connected to this SC and clone
            scismaps= SCISMap.objects.filter(strategyComponent=sc)
            for scismap in scismaps:
                # get the IS on the end of this map
                intsel = scismap.interventionSelector

                # clone it
                new_intsel = InterventionSelector.getActual(intsel,new_strat)
                # the new actual IS should get the same generic parent as the one we're copying from
                new_intsel.genericParent = intsel.genericParent
                new_intsel.save()
                # clone the map
                new_scismap = SCISMap(strategyComponent=new_sc, interventionSelector=new_intsel, isActive=scismap.isActive, config= scismap.config, myStrategy=new_strat)
                new_scismap.save()
                # clone all the intervention selectors params
                for p in intsel.getParams(sc):
                    new_isparam = InterventionSelectorParam.getInstanceFromActualParam(p,new_strat)
                    new_isparam.scismap = new_scismap
                    new_isparam.save()
        new_strat.login = new_scs[0]
        new_strat.lesson = new_scs[1]
        new_strat.tutor = new_scs[2]
        new_strat.save()

        return new_strat


    # Clone its sub-structure objects



# Remove an actual strategy (not a generic one).
# This relies on all the substructure to have a mystrategy field which points to the strategy we are deleting.
def removeStrategy (strategy):
    # In a single transaction get rid of the whole structure of a strategy from the bottom up to avoid
    # tripping over foreign keys.
    with transaction.atomic():
        isParams = InterventionSelectorParam.objects.filter(myStrategy=strategy)
        scParams = StrategyComponentParam.objects.filter(myStrategy=strategy)
        scpmaps = SCParamMap.objects.filter(myStrategy=strategy)
        scismaps = SCISMap.objects.filter(myStrategy=strategy)
        intsels = InterventionSelector.objects.filter(myStrategy=strategy)
        scs = [strategy.lesson, strategy.tutor, strategy.login]
        # first we get rid of IS params because they point to SCIS maps
        for isp in isParams:
            isp.delete()
        # now get rid of scis maps because they point to IS and SC rows
        for m in scismaps:
            m.delete()
        # get rid of sc param maps because they point to SC Params and SC
        for m in scpmaps:
            m.delete()
        # get rid of sc params (they point to nothing)
        for scp in scParams:
            scp.delete()
        # get rid of the intervention selectors (they point to nothing)
        for i in intsels:
            i.delete()
        # get rid of the strategy because it has ids of its SCs
        strategy.delete()

        # get rid of SC s
        for sc in scs:
            if sc:
                sc.delete()

def deleteGenericStrategy (strategy):
    with transaction.atomic():
        isParams = []
        scParams = []
        scpmaps = []
        scismaps = []
        scs = [strategy.lesson, strategy.tutor, strategy.login]
        for sc in scs:
            maps = SCParamMap.objects.filter(strategyComponent=sc)
            for m in maps:
                scpmaps.append(m)
                scParams.append(m.param)
            maps = SCISMap.objects.filter(strategyComponent=sc)
            for m in maps:
                scismaps.append(m)
                params = InterventionSelectorParam.objects.filter(scismap=m)
                for p in params:
                    isParams.append(p)
        # first we get rid of IS params because they point to SCIS maps
        for isp in isParams:
            isp.delete()
        # now get rid of scis maps because they point to IS and SC rows
        for m in scismaps:
            m.delete()
        # get rid of sc param maps because they point to SC Params and SC
        for m in scpmaps:
            m.delete()
        # get rid of sc params (they point to nothing)
        for scp in scParams:
            scp.delete()

        # get rid of the strategy because it has ids of its SCs
        strategy.delete()

        # get rid of SC s
        for sc in scs:
            if sc:
                print("deleting " + str(sc.id))
                sc.delete()
                print("deleted " + str(sc.id))


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

def validate_scismaps (sc, type, il):
    strbuf = ""
    scismaps = SCISMap.objects.filter(strategyComponent=sc)
    for m in scismaps:
        insel = m.interventionSelector
        is_param_bases = insel.getBaseParams()
        n_base_isparams = is_param_bases.__len__()
        is_param_scs = m.getISParams()
        n_sc_isparams = is_param_scs.__len__()
        if (type == 'generic' and n_base_isparams != n_sc_isparams):
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

def validate_strategy_scismaps (strat, type,il):
    sc_login = strat.login
    sc_lesson = strat.lesson
    sc_tutor = strat.tutor
    msg = ""
    msg += validate_scismaps (sc_login,type,il)
    msg += validate_scismaps (sc_lesson,type,il)
    msg += validate_scismaps (sc_tutor,type,il)
    return msg



# Make sure the sc has only the expected params and that they are all present
def validate_sc_2 (sc, expected_params, type, il):
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
def validate_sc_params (strat, type, il):

    sc = strat.lesson
    strbuf = ""
    lesson_params = [ 'maxTimeInTopicSecs', 'contentFailureThreshold', 'topicMastery', 'minNumberProbs', 'maxNumberProbs', 'minTimeInTopicSecs']
    strbuf += validate_sc_2(sc,lesson_params,type, il)

    sc = strat.tutor
    tutor_params = [ 'studentModelClass', 'problemSelectorClass', 'reviewModeProblemSelectorClass', 'challengeModeProblemSelectorClass', 'problemReuseIntervalSessions', 'problemReuseIntervalDays', 'displayMyProgressPage', 'hintSelectorClass','difficultyRate']
    strbuf += validate_sc_2(sc,tutor_params,type,il)

    return strbuf



def printSC (sc, strat):
    msg = "&nbsp;"*2 + "SC: " + str(sc.pk) + " " + sc.name + " type:" + sc.type + "<br>"
    maps = SCParamMap.objects.filter(strategyComponent=sc, myStrategy=strat).all()
    for m in maps:
        msg += "&nbsp;"*8  + "SCParamMap " + str(m.pk) + "<br>"
        msg += printSCParam(m.param)
    maps = SCISMap.objects.filter(strategyComponent=sc, myStrategy=strat)
    for scismap in maps:
        msg += "&nbsp;"*8 + "SCISMap " + str(scismap.pk) + "<br>"
        isActive = scismap.isActive
        if not isActive:
            isActive = False
        msg += printIS(scismap.interventionSelector,sc,isActive)
    return msg



def printSCParam (p):
    return "&nbsp;"*8 +"Param " + str(p.pk) + " " + p.name + "=" + p.value + " active=" + str(p.isActive)  + "<br>"

def printIS (intsel, sc, isActive):

    msg = "&nbsp;"*8 +"IS: " + str(intsel.pk) + " " + intsel.name + " active=" + str(isActive) + "<br>"
    for p in intsel.getParams(sc):
        msg += printISParam(p)
    return msg

def printISParam (p):
    msg = "&nbsp;"*16 +"Param: " + str(p.pk) + " " + p.name + "=" + p.value[0: min(15, len(p.value))] + " active=" + str(p.isActive) + "<br>"
    return msg


def printStrategy (strat):
    print("Strategy : " + str(strat.pk))
    type = "actual" if strat.isActual() else "generic"
    msg = type + " strategy (" + str(strat.pk) + ") " + strat.name + "<br>"
    scs = [strat.login, strat.lesson, strat.tutor]
    for sc in scs:
        if type == 'actual':
            msg += printSC(sc,strat)
        else:
            msg += printSC(sc,None)

    return msg

def validateStrategy (strat):
    msg = printStrategy(strat)
    type = "actual" if strat.isActual() else "generic"
    msg += "Validating "+type+" strategy (" + str(strat.pk) + ") " + strat.name + "<br>"
    msg += validate_sc_params(strat,type,4)
    msg += '--<br>'
    msg += validate_strategy_scismaps(strat,type,4)
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

