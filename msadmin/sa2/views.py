from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from .classops import *


# Create your views here.
def strategy_list(request):
    strategies = Strategy.objects.all()

    return render(request, 'msadmin/sa/strategy_list.html', {'strategies': strategies})

# Shows the main page of the site
def main(request):
    return render(request, 'msadmin/sa/main.html', {})



def sc_detail (request, pk):
    sc = get_object_or_404(StrategyComponent, pk=pk)
    # sc = StrategyComponent.ojects.get(pk=pk)
    return render(request, 'msadmin/sa/strategycomponent.html', {'strategycomponent': sc})

# Create your views here.
def class_list(request):
    classes = Class.objects.all().order_by('teacher', 'name')
    teachers = Teacher.objects.all().order_by('lname', 'fname')
    # classes = Class.objects.filter(teacher='David Marshall').order_by('teacher', 'name')

    return render(request, 'msadmin/sa/class_list.html', {'classes': classes, 'teachers': teachers, 'teacherId': None})

# Create your views here.
def class_list_by_teacher(request, teacherId):

    teacher = None
    if teacherId != None and teacherId != 'All':
        teacher = Teacher.objects.get(pk=teacherId)
        teacherId = int(teacherId)
    teachers = Teacher.objects.all().order_by('lname', 'fname')
    if teacher != None:
        classes = Class.objects.filter(teacherId=teacherId).order_by('teacher', 'name')
    else:
        classes = Class.objects.all().order_by('teacher', 'name')

    return render(request, 'msadmin/sa/class_list.html', {'classes': classes, 'teacherId': teacherId, 'teachers': teachers})



def class_detail (request, pk):
    # csrfContext = RequestContext(request)
    c = get_object_or_404(Class, pk=pk)
    teacherId= c.teacherId
    classes = Class.objects.filter(teacherId=teacherId).order_by('name')
    classid = c.id
    teachers = Teacher.objects.all().order_by('lname','fname')
    # Get all the strategies that exist for this class
    class_strats = Strategy.objects.filter(aclass=c)
    strats = []
    # put in a standard list
    for s in class_strats:
        strats.append(s)
    # get all the generic strategies
    allstrats = Strategy.objects.all()
    otherstrats = []
    # add all the generics to a standard list and then remove the ones that are already in use for the class
    for s in allstrats:
        otherstrats.append(s)
    for s in strats:
        otherstrats.remove(s)
    loginSCs = StrategyComponent.objects.filter(type=StrategyComponent.LOGIN)
    lessonSCs = StrategyComponent.objects.filter(type=StrategyComponent.LESSON)
    tutorSCs = StrategyComponent.objects.filter(type=StrategyComponent.TUTOR)
    lcs = LC.objects.all()
    # sc = StrategyComponent.ojects.get(pk=pk)
    return render(request, 'msadmin/sa/class.html',
                  {'class': c, 'strategies' : class_strats, 'otherStrategies': otherstrats, 'loginSCs': loginSCs, 'lessonSCs': lessonSCs, 'tutorSCs' : tutorSCs, 'lcs': lcs, 'myclasses': classes, 'teachers': teachers, 'curTeacherId': teacherId })




def strategy_detail (request, pk):
    strat = get_object_or_404(Strategy, pk=pk)
    return render(request, 'msadmin/sa/strategy.html', {'strategy': strat})

# Given a strategy-component, return a list of lists.
# like: [ [intervSel-1 [param-1, param-2,...]],  [intervSel-2 [param-1, param-2... ]] ]
#  The params are based on the class.
'''
def getInterventionSelectorInfo (aclass, stratComp):
    res = []
    for sel in stratComp.interventionSelectors.all():
        params = []
        # set the active true/false status of the intervention selector so that the GUI knows if its on or off.
        sel.setActiveStatus(aclass, stratComp)
        baseISParams = sel.getBaseParams()
        # for p in sel.getParams(stratComp):
        for p in baseISParams:
            cp = ClassISParam.objects.get(isParam=p, theClass=aclass)
            params.append(cp)
        res.append([sel, params])
    return res
'''

def configure_class_strategy (request, classId, strategyId):
    cl = get_object_or_404(Class, pk=classId)
    # st = get_object_or_404(Strategy, pk=strategyId)
    clstrat = get_object_or_404(Strategy, pk=strategyId)

    return render(request, 'msadmin/sa/class_strategy2.html',
                  {'class': cl, 'classStrategy': clstrat})

def add_class_strategy (request, classId, strategyId):
    c = get_object_or_404(Class, pk=classId)
    s = get_object_or_404(Strategy, pk=strategyId)

    # Copies various items from the strategy into tables specific to this class
    makeActualStrategyFromGeneric(c, s)
    return redirect("class_detail",pk=classId)


# handles a POST request coming from the class page.  It adds a new custom strategy to the class and then redirects
# to the class detail page to show the new list of strategies that the class has.
def add_class_custom_strategy (request, classId):

    # return render_to_response('foo.html', csrfContext)
    c = get_object_or_404(Class, pk=classId)
    if request.method == "POST":
        post = request.POST
        strategyName = post['strategyName']
        descr = post['strategyDescr']
        loginSCId = post['loginSCId']
        lessonSCId = post['lessonSCId']
        tutorSCId = post['tutorSCId']
        lcId = post['lcId']
        loginSC = get_object_or_404(StrategyComponent, pk=loginSCId)
        lessonSC = get_object_or_404(StrategyComponent, pk=lessonSCId)
        tutorSC = get_object_or_404(StrategyComponent, pk=tutorSCId)
        lc = get_object_or_404(LC,pk=lcId)
        createCustomStrategyForClass(c,strategyName,loginSC,lessonSC,tutorSC, lc,descr)

    return redirect("class_detail",pk=classId)

# handles a POST request coming from the class page.  It copies a strategy from another class to this class.
def add_class_other_class_strategy (request, classId, otherClassId, stratId):

    # return render_to_response('foo.html', csrfContext)
    c = get_object_or_404(Class, pk=classId)
    strat = get_object_or_404(Strategy, pk=stratId)

    copyStrategyFromOtherClass(c,strat)

    return redirect("class_detail",pk=classId)

def remove_class_strategy (request, classId, strategyId):

    c = get_object_or_404(Class, pk=classId)
    s = get_object_or_404(Strategy, pk=strategyId)
    # gets rid of rows in tables that have specific information about this strategy for the class
    removeStrategy(s)
    return redirect("class_detail",pk=classId)


# support for AJAX call from a checkbox next to a intervention-selector node in the jstree
# It will set the isActive field in the SCISMap table to the isActive value
def class_activate_is (request, classId, scId, isId, isActive):
    sc = get_object_or_404(StrategyComponent, pk=scId)
    insel = get_object_or_404(InterventionSelector, pk=isId)
    setting = isActive=='true'
    scismap = SCISMap.objects.get(strategyComponent=sc,interventionSelector=insel)
    scismap.isActive = setting
    scismap.save()
    return HttpResponse()

def validate_generic (request):
    return HttpResponse(validateGenericStructure())

def validate_class_tutoring (request):
    return validateClassTutoringStrategies(request)

def test (request):
    return render(request, 'msadmin/test.html')

def blee (request):
    return HttpResponse("Blee")