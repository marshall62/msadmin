from django.shortcuts import render, get_object_or_404
from .models import StrategyComponent
from .models import Strategy
from .models import Class

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
    classes = Class.objects.all()

    return render(request, 'msadmin/class_list.html', {'classes': classes})

def class_detail (request, pk):
    c = get_object_or_404(Class, pk=pk)
    classid = c.id
    # lookup a the class strategies
    strats = Strategy.objects.filter(classstrategymap__myclass__id=classid)
    # sc = StrategyComponent.ojects.get(pk=pk)
    return render(request, 'msadmin/class.html', {'class': c, 'strategies' : strats})

def strategy_detail (request, pk):
    strat = get_object_or_404(Strategy, pk=pk)
    return render(request, 'msadmin/strategy.html', {'strategy': strat})
