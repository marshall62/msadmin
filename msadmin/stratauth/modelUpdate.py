from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from msadmin.stratauth.models import Class
from msadmin.stratauth.models import ClassISParam
from msadmin.stratauth.models import ClassSCISMap
from msadmin.stratauth.models import ClassSCParam
from msadmin.stratauth.models import InterventionSelector
from msadmin.stratauth.models import SCISMap
from msadmin.stratauth.models import StrategyComponent, Strategy_Class, LC, SC_Class


# An AJAX post request coming from a dialog box that allows edit of class-is-param.
def save_is_param (request, isParamId):
    if request.method == "POST":
        post = request.POST
        newVal = post['value']
        isActive = post['isActive']
        p = get_object_or_404(ClassISParam, pk=isParamId)
        p.value = newVal
        p.isActive = isActive == 'true'
        p.save()
    return JsonResponse({"isParamId": isParamId, "name": p.name, "value": newVal, "isActive": p.isActive})


# An AJAX post request coming from a dialog box that allows edit of class-sc-param.
def save_sc_param (request, scParamId):
    if request.method == "POST":
        post = request.POST
        newVal = post['value']
        isActive = post['isActive']
        p = get_object_or_404(ClassSCParam, pk=scParamId)
        p.value = newVal
        p.isActive = isActive == 'true'
        p.save()
    return JsonResponse({"scParamId": scParamId, "name": p.name, "value": newVal, "isActive": p.isActive})

# An AJAX post request coming from a dialog box that allows edit of class-sc_is_map
def save_is (request, isId, strategyId):
    if request.method == "POST":
        post = request.POST
        config = post['config']
        isActive = post['isActive']
        classId = post['classId']
        scId = post['scId']
        c = get_object_or_404(Class, pk=classId)
        sc = get_object_or_404(StrategyComponent, pk=scId)
        insel = get_object_or_404(InterventionSelector, pk=isId)
        stratClass = get_object_or_404(Strategy_Class, pk=strategyId)
        scismap = get_object_or_404(SCISMap, strategyComponent=sc, interventionSelector=insel)
        sc_class = get_object_or_404(SC_Class, sc=sc, theClass=c, classStrategy=stratClass)
        cl_scismap = get_object_or_404(ClassSCISMap, ismap=scismap, theClass=c, classSC=sc_class)
        cl_scismap.isActive = isActive == 'true'
        cl_scismap.config = config
        cl_scismap.save()
    return JsonResponse({"isId": isId, "isActive": cl_scismap.isActive})

# An AJAX post request coming from the tree editor when checkbox next to an isParam is clicked
# if checkbox is selected, isActive='true', o/w = 'false'
# sets the class_is_param.isActive field accordingly
def save_is_param_active (request, isParamId):
    if request.method == "POST":
        post = request.POST
        status = post['active']
        p = get_object_or_404(ClassISParam, pk=isParamId)
        p.isActive = status == 'true'
        p.save()
    return JsonResponse({"isParamId": isParamId})

# An AJAX post request coming from the tree editor when checkbox next to an scParam is clicked
# if checkbox is selected, isActive='true', o/w = 'false'
# sets the class_sc_param.isActive field accordingly
def save_sc_param_active (request, scParamId):
    if request.method == "POST":
        post = request.POST
        status = post['active']
        p = get_object_or_404(ClassSCParam, pk=scParamId)
        p.isActive = status == 'true'
        p.save()
    return JsonResponse({"isParamId": scParamId})

# An AJAX post request coming from the tree editor when checkbox next to an interventionSelector is clicked
# if checkbox is selected, isActive='true', o/w = 'false'
# sets the class_sc_is_map.isActive field accordingly
def save_intervSel_active (request, isId):
    if request.method == "POST":
        post = request.POST
        status = post['active']
        classId = post['classId']
        scId = post['scId']
        stratClassId = post['strategyClass']
        c = get_object_or_404(Class, pk=classId)
        stratClass = get_object_or_404(Strategy_Class,pk=stratClassId)
        sc = get_object_or_404(StrategyComponent, pk=scId)
        sc_class = SC_Class.objects.filter(theClass=c,sc=sc,classStrategy=stratClass)
        insel = get_object_or_404(InterventionSelector, pk=isId)
        scismap = get_object_or_404(SCISMap, strategyComponent=sc, interventionSelector=insel)
        cl_scismap = get_object_or_404(ClassSCISMap, ismap=scismap, theClass=c, classSC=sc_class)
        cl_scismap.isActive = status == 'true'
        cl_scismap.save()
    return JsonResponse({"id": isId})

# An Ajax POST when the strategy dialog is saved.  Will set the Strategy_class lc object.
def save_strategy (request, id):
    if request.method == "POST":
        post = request.POST
        lcid = post['lcid']
        name = post['name']
        descr = post['description']
        stratclass = get_object_or_404(Strategy_Class,pk=id)
        lc = get_object_or_404(LC,pk=lcid)
        stratclass.lc = lc
        stratclass.name = name
        stratclass.description = descr
        stratclass.save()
        return JsonResponse({"id": id})
