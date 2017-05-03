from django.shortcuts import render, get_object_or_404
from .models import StrategyComponent
from .models import Strategy

# Create your views here.
def strategy_list(request):
    strategies = Strategy.objects.all()

    return render(request, 'msadmin/strategy_list.html', {'strategies': strategies})

def sc_detail (request, pk):
    sc = get_object_or_404(StrategyComponent, pk=pk)
    # sc = StrategyComponent.ojects.get(pk=pk)
    return render(request, 'msadmin/strategycomponent.html', {'strategycomponent': sc})