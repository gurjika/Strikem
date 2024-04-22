from django.shortcuts import render
from .models import Invitation, MatchMake, Matchup
# Create your views here.


def poolhouse(request, poolhouse):
    return render(request, 'poolstore/poolhouse.html', {'poolhouse': poolhouse})


def matchmakings(request):
    matches = MatchMake.objects.all()

    invites = Invitation.objects.filter(player_invited__user=request.user)


    context = {
        'invites': invites,
        'matches': matches
    }
    
    return render(request, 'poolstore/matchmake.html', context)


def matchup(request, matchup_id):
    matchup = Matchup.objects.get(id=matchup_id)
    context = {'matchup': matchup}
    return render(request, 'poolstore/matchup.html', context)