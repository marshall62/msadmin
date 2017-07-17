from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from msadmin.forms import ClassForm
from .models import StrategyComponent
from .models import Strategy
from .models import Class
from .models import SCISMap
from .dbops.classops import *

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
    c = get_object_or_404(Class, pk=pk)
    classid = c.id
    class_strats = Strategy_Class.objects.filter(theClass=c)
    strats = []
    for cs in class_strats:
        strats.append(cs.strategy)
    allstrats = Strategy.objects.all()
    otherstrats = []
    for s in allstrats:
        otherstrats.append(s)
    for s in strats:
        otherstrats.remove(s)

    # sc = StrategyComponent.ojects.get(pk=pk)
    return render(request, 'msadmin/class.html', {'class': c, 'strategies' : strats, 'otherStrategies': otherstrats})




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
    st = get_object_or_404(Strategy, pk=strategyId)
    clstrat = Strategy_Class.objects.get(theClass=cl, strategy=st)
    # No longer send down objects through variables.  Page makes AJAX request to get JSON to populate a tree

    # loginComp = st.login
    # tutorComp = st.tutor
    # lessonComp = st.lesson
    # # d maps isel ids -> a dictionary of param.id -> param
    # loginISParams=getInterventionSelectorInfo(cl,loginComp)
    # lessonISParams=getInterventionSelectorInfo(cl,lessonComp)
    # tutorISParams=getInterventionSelectorInfo(cl,tutorComp)
    return render(request, 'msadmin/class_strategy2.html',
                  {'class': cl, 'strategy': st, 'classStrategy': clstrat})
    # 'loginSC': loginComp, 'tutorSC': tutorComp, 'lessonSC': lessonComp,
    #                'loginInfo': loginISParams, 'lessonInfo':lessonISParams, 'tutorInfo':tutorISParams})

def add_class_strategy (request, classId, strategyId):
    c = get_object_or_404(Class, pk=classId)
    s = get_object_or_404(Strategy, pk=strategyId)

    # Copies various items from the strategy into tables specific to this class
    copyStrategyToClass(c,s)
    return class_detail(request,classId)

def remove_class_strategy (request, classId, strategyId):
    # TODO add stuff to the db
    c = get_object_or_404(Class, pk=classId)
    s = get_object_or_404(Strategy, pk=strategyId)
    # gets rid of rows in tables that have specific information about this strategy for the class
    removeStrategyFromClass(c,s)
    return class_detail(request,classId)


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