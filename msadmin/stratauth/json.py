from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from msadmin.stratauth.models import Class
from msadmin.stratauth.models import ClassISParam
from msadmin.stratauth.models import ClassSCISMap
from msadmin.stratauth.models import InterventionSelector
from msadmin.stratauth.models import SCISMap
from msadmin.stratauth.models import Strategy
from msadmin.stratauth.models import StrategyComponent, ClassSCParam, LC, Strategy_Class, SC_Class


def get_strategy_json (request, classId, strategyId):
    c = get_object_or_404(Class, pk=classId)
    s = get_object_or_404(Strategy, pk=strategyId)
    return JsonResponse(s.getJSON(c), safe=False)

# strategyId is the id of a Strategy_class row
def get_strategy_json (request, classId, strategyId):
    c = get_object_or_404(Class, pk=classId)
    stratClass = get_object_or_404(Strategy_Class, pk=strategyId)
    return JsonResponse(stratClass.getJSON(), safe=False)

# Given the id of a ClassISParam return JSON that represents all its detail
def get_is_param_json (request, isParamId):
    p = get_object_or_404(ClassISParam, pk=isParamId)
    d = {}
    d["id"] = isParamId
    d["name"] = p.name
    d["value"] = p.value
    possibleVals = []
    for v in p.getPossibleValues():
        possibleVals.append(v.value)

    d["possibleValues"] = possibleVals
    d["description"] = p.isParam.description
    d["isActive"] =  p.isActive
    d["interventionSelectorName"] = p.isParam.interventionSelector.name
    return JsonResponse(d)

def get_sc_param_json (request, scParamId):
    p = get_object_or_404(ClassSCParam, pk=scParamId)
    d = {}
    d["id"] = scParamId
    d["name"] = p.name
    d["value"] = p.value
    # possibleVals = []
    # for v in p.getPossibleValues():
    #     possibleVals.append(v.value)
    #
    # d["possibleValues"] = possibleVals
    d["description"] = p.scParam.description
    d["isActive"] =  p.isActive
    return JsonResponse(d)


def get_is (request, classId, isId, scId, strategyId):
    c = get_object_or_404(Class, pk=classId)
    isel = get_object_or_404(InterventionSelector, pk=isId)
    sc = get_object_or_404(StrategyComponent, pk=scId)
    stratClass = get_object_or_404(Strategy_Class, pk=strategyId)
    scClass = get_object_or_404(SC_Class, theClass=c, sc=sc, classStrategy=stratClass)
    scismap = get_object_or_404(SCISMap, interventionSelector=isel, strategyComponent=sc)
    m = get_object_or_404(ClassSCISMap, theClass=c, ismap=scismap, classSC=scClass)
    insel = get_object_or_404(InterventionSelector,pk=isId)
    d= {}
    d['name'] = insel.name
    d['config'] = m.config
    d['description'] = insel.description
    d['isActive'] = m.isActive
    d['id'] = isId
    return JsonResponse(d)

def get_all_lcs (request):
    lcs = LC.objects.all()
    d = {}
    for lc in lcs:
        d[lc.id] = lc.name + ':' + lc.charName
    return JsonResponse(d)

def get_strategy_lcs (request, id):
    strat = get_object_or_404(Strategy_Class,pk=int(id))
    lcs = LC.objects.all()
    # build a dictionary with the lcid of the strategy's lcid and a sub-dictionary containing all the other lc ids (to put in a pulldown menu)
    d = {}
    d['lcid'] = strat.lc.id
    lcd = {}
    for lc in lcs:
        lcd[lc.id] = lc.name + ':' + lc.charName
    d['all_lcs'] = lcd
    return JsonResponse(d)

# Return  JSON that is a like [ {id:34, teacher:'David marshall', name:'My Class'}, ... ] style JSON objects
def class_list_by_teacher(request, teacher):

    json_arr = []
    if teacher == 'All':
        classes = Class.objects.all().order_by('teacher', 'name')
    else:
        classes = Class.objects.filter(teacher=teacher).order_by('name')

    for c in classes:
        json_arr.append(c.toJSON())

    return JsonResponse(json_arr,safe=False)

def get_teacher_classes (request, teacherId) :
    json_arr = []
    classes = Class.objects.filter(teacherId=teacherId).order_by('name')
    for c in classes:
        json_arr.append(c.toJSON())

    return JsonResponse(json_arr,safe=False)

def get_class_strategies (request, classId) :
    json_arr = []
    c = get_object_or_404(Class, pk=classId)
    strats = Strategy_Class.objects.filter(theClass=c).order_by('name')
    for s in strats:
        json_arr.append(s.getSimpleJSON())

    return JsonResponse(json_arr,safe=False)

