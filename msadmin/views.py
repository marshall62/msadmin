from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.shortcuts import redirect
from django.template import RequestContext

from msadmin.forms import ClassForm
from .models import StrategyComponent
from .models import Strategy
from .models import Class
from .models import SCISMap
from .dbops.classops import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt


# Create your views here.
def strategy_list(request):
    strategies = Strategy.objects.all()

    return render(request, 'msadmin/strategy_list.html', {'strategies': strategies})

def sc_detail (request, pk):
    sc = get_object_or_404(StrategyComponent, pk=pk)
    # sc = StrategyComponent.ojects.get(pk=pk)
    return render(request, 'msadmin/strategycomponent.html', {'strategycomponent': sc})

# Create your views here.
def class_list(request):
    classes = Class.objects.all().order_by('teacher', 'name')
    teachers = Teacher.objects.all().order_by('lname', 'fname')
    # classes = Class.objects.filter(teacher='David Marshall').order_by('teacher', 'name')

    return render(request, 'msadmin/class_list.html', {'classes': classes, 'teachers': teachers})

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

    return render(request, 'msadmin/class_list.html', {'classes': classes, 'teacherId': teacherId, 'teachers': teachers})



def class_detail (request, pk):
    # csrfContext = RequestContext(request)
    c = get_object_or_404(Class, pk=pk)
    classid = c.id
    # Get all the strategies that exist for this class
    class_strats = Strategy_Class.objects.filter(theClass=c)
    strats = []
    # put in a standard list
    for cs in class_strats:
        if cs.strategy_id != None:
            strats.append(cs.strategy)
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
    return render(request,'msadmin/class.html',
                              {'class': c, 'strategies' : class_strats, 'otherStrategies': otherstrats, 'loginSCs': loginSCs, 'lessonSCs': lessonSCs, 'tutorSCs' : tutorSCs, 'lcs': lcs })




def strategy_detail (request, pk):
    strat = get_object_or_404(Strategy, pk=pk)
    return render(request, 'msadmin/strategy.html', {'strategy': strat})

# Given a strategy-component, return a list of lists.
# like: [ [intervSel-1 [param-1, param-2,...]],  [intervSel-2 [param-1, param-2... ]] ]
#  The params are based on the class.
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

def configure_class_strategy (request, classId, strategyId):
    cl = get_object_or_404(Class, pk=classId)
    # st = get_object_or_404(Strategy, pk=strategyId)
    clstrat = get_object_or_404(Strategy_Class, pk=strategyId)

    return render(request, 'msadmin/class_strategy2.html',
                  {'class': cl, 'classStrategy': clstrat})

def add_class_strategy (request, classId, strategyId):
    c = get_object_or_404(Class, pk=classId)
    s = get_object_or_404(Strategy, pk=strategyId)

    # Copies various items from the strategy into tables specific to this class
    copyStrategyToClass(c,s)
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

def remove_class_strategy (request, classId, strategyId):
    # TODO add stuff to the db
    c = get_object_or_404(Class, pk=classId)
    s = get_object_or_404(Strategy_Class, pk=strategyId)
    # gets rid of rows in tables that have specific information about this strategy for the class
    removeStrategyFromClass(c,s)
    return redirect("class_detail",pk=classId)


# support for AJAX call from a checkbox next to a intervention-selector node in the jstree
# It will set the isActive field in the class_sc_is_map table to true or false.
def class_activate_is (request, classId, scId, isId, isActive):
    c = get_object_or_404(Class, pk=classId)
    sc = get_object_or_404(StrategyComponent, pk=scId)
    insel = get_object_or_404(InterventionSelector, pk=isId)
    setting = isActive=='true'
    scismap = SCISMap.objects.get(strategyComponent=sc,interventionSelector=insel)
    cscimap = ClassSCISMap.objects.get(ismap=scismap,theClass=c)
    cscimap.isActive = setting
    cscimap.save()
    return HttpResponse()

def test (request):
    return render(request,'msadmin/test.html')

def blee (request):
    return HttpResponse("Blee")