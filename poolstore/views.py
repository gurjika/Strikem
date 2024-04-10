from django.shortcuts import render
from .models import MatchMake
# Create your views here.


def poolhouse(request, poolhouse):
    return render(request, 'poolstore/poolhouse.html', {'poolhouse': poolhouse})


def matchmakings(request):
    matches = MatchMake.objects.all()
    context = {
        'matches': matches
    }
    
    return render(request, 'poolstore/matchmake.html', context)