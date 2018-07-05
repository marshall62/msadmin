from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from msadmin.sa2.models import Class, InterventionSelectorParam, StrategyComponentParam

from msadmin.sa2.models import InterventionSelector
from msadmin.sa2.models import SCISMap
from msadmin.sa2.models import Strategy
from msadmin.sa2.models import StrategyComponent, LC


def get_strategy_json (request, classId, strategyId):
    c = get_object_or_404(Class, pk=classId)
    s = get_object_or_404(Strategy, pk=strategyId)
    return JsonResponse(s.getJSON(c), safe=False)

def get_sc_json (request, scId):
    sc = get_object_or_404(StrategyComponent, pk=scId)
    d = {}
    d["id"] = sc.id
    d["name"] = sc.name
    d["description"] = sc.description
    d["briefDescr"] = sc.briefDescr
    return JsonResponse(d)

# Given the id of a ISParam return JSON that represents all its detail
def get_is_param_json (request, isParamId):
    p = get_object_or_404(InterventionSelectorParam, pk=isParamId)
    d = {}
    d["id"] = isParamId
    d["name"] = p.name
    d["value"] = p.value
    possibleVals = p.getPossibleValues()
    d["possibleValues"] = possibleVals
    d["description"] = p.getDescription()
    d["isActive"] =  p.isActive
    return JsonResponse(d)

def get_sc_param_json (request, scParamId):
    p = get_object_or_404(StrategyComponentParam, pk=scParamId)
    d = {}
    d["id"] = scParamId
    d["name"] = p.name
    d["value"] = p.value
    # possibleVals = []
    # for v in p.getPossibleValues():
    #     possibleVals.append(v.value)
    #
    # d["possibleValues"] = possibleVals
    d["description"] = p.description
    d["isActive"] =  p.isActive
    return JsonResponse(d)


def get_is (request, classId, isId, scId, strategyId):
    isel = get_object_or_404(InterventionSelector, pk=isId)
    sc = get_object_or_404(StrategyComponent, pk=scId)
    scismap = get_object_or_404(SCISMap, interventionSelector=isel, strategyComponent=sc)

    d= {}
    d['name'] = isel.name
    d['config'] = scismap.config
    d['description'] = isel.description
    d['isActive'] = scismap.isActive
    d['id'] = isId
    return JsonResponse(d)

def get_all_lcs (request):
    lcs = LC.objects.all()
    d = {}
    for lc in lcs:
        d[lc.id] = lc.name + ':' + lc.charName
    return JsonResponse(d)

def get_strategy_lcs (request, id):
    strat = get_object_or_404(Strategy,pk=int(id))
    lcs = LC.objects.all()
    # build a dictionary with the lcid of the strategy's lcid and a sub-dictionary containing all the other lc ids (to put in a pulldown menu)
    d = {}
    d['lcid'] = strat.lc.id if strat.lc else None
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
    strats = Strategy.objects.filter(aclass=c).order_by('name')
    for s in strats:
        json_arr.append(s.getSimpleJSON())

    return JsonResponse(json_arr,safe=False)

