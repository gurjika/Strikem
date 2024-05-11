from django.shortcuts import get_object_or_404, render
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
    matchup = get_object_or_404(Matchup, id=matchup_id)

    if matchup.player_accepting.user == request.user:
        opponent = matchup.player_inviting

    elif matchup.player_inviting.user == request.user:   
        opponent = matchup.player_accepting

    else:
        raise PermissionDenied()
    

    
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
               'paginator': paginator,
               'opponent': opponent}
    


    if request.htmx:

        load_type = request.GET.get('load_type')
        if load_type == 'load-matchup':

            return render(request, 'poolstore/partials/matchup_chat.html', context)
        
        return render(request, 'poolstore/partials/matchup-elements.html', context)
    

    all_matchups = Matchup.objects.filter(messages__receiver__user=request.user).distinct()
    context['matchups'] = all_matchups
    return render(request, 'poolstore/matchup.html', context)

    
    





class PoolHouseListView(ListView):
    queryset = PoolHouse.objects.all()
    template_name = 'poolstore/poolhouses.html'
    context_object_name = 'poolhouses'


def home(request):
    
    return render(request, 'poolstore/home.html')