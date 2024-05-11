from django.shortcuts import render
from .models import Invitation, MatchMake, Matchup, PoolHouse, Message
from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
# Create your views here.



def poolhouse(request, poolhouse):
    return render(request, 'poolstore/poolhouse.html', {'poolhouse': poolhouse})

@login_required
def matchmakings(request):
    matches = MatchMake.objects.all()

    invites = Invitation.objects.filter(player_invited__user=request.user)


    context = {
        'invites': invites,
        'matches': matches
    }
    
    return render(request, 'poolstore/matchmake.html', context)

@login_required
def matchup(request, matchup_id):
    matchup = Matchup.objects.get(id=matchup_id)
    messages = Message.objects.filter(matchup=matchup).select_related('sender').select_related('sender__user').select_related('matchup').order_by('-time_sent')
    paginator = Paginator(messages, 10)
    page_number = request.GET.get("page")
    


    page_obj = paginator.get_page(page_number)

    messages_to_display = list(page_obj)[::-1]

    context = {'matchup': matchup, 
               'matchup_messages': messages_to_display, 
               'page_obj':page_obj, 
               'matchup_id': matchup_id, 
               'paginator': paginator}
    
    if request.htmx:
        return render(request, 'poolstore/partials/matchup-elements.html', context)
    
    if matchup.player_accepting.user == request.user:
        opponent = matchup.player_inviting

    elif matchup.player_inviting.user == request.user:
        opponent = matchup.player_accepting

    else:
        raise PermissionDenied()

    context['opponent'] = opponent

    all_matchups = Matchup.objects.filter(Q(player_inviting__user=request.user) | Q(player_accepting__user=request.user))
    context['all_matchups'] = all_matchups

    return render(request, 'poolstore/matchup.html', context)


class PoolHouseListView(ListView):
    queryset = PoolHouse.objects.all()
    template_name = 'poolstore/poolhouses.html'
    context_object_name = 'poolhouses'


def home(request):
    
    return render(request, 'poolstore/home.html')