from django.shortcuts import get_object_or_404, render
from .models import Invitation, MatchMake, Matchup, Player, PoolHouse, Message
from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models import Max
from django.db.models import Prefetch

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
    
    matchup = Matchup.objects.select_related('player_inviting__user').select_related('player_accepting__user').filter(id=matchup_id).first()
    if matchup.player_accepting.user == request.user:
        opponent = matchup.player_inviting

    elif matchup.player_inviting.user == request.user:   
        opponent = matchup.player_accepting

    else:
        raise PermissionDenied()
    
    
    messages = Message.objects.select_related('sender').select_related('sender__user').filter(matchup=matchup).order_by('-time_sent')
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
    

    all_matchups = Matchup.objects.prefetch_related(
    Prefetch('messages', queryset=Message.objects.all().select_related('sender__user')),
        'player_inviting__user',
        'player_accepting__user'
    ).filter(Q(player_inviting=request.user.player) | Q(player_accepting=request.user.player)
    ).annotate(latest_message_time=Max('messages__time_sent')).order_by('-latest_message_time')

    last_messages = []

    for matchup in all_matchups:
        last_messages.append(list(matchup.messages.all())[-1])
    
    matchups_with_last_message = zip(last_messages, list(all_matchups))

    context['matchups'] = matchups_with_last_message
    return render(request, 'poolstore/matchup.html', context)

    



class PoolHouseListView(ListView):
    queryset = PoolHouse.objects.all()
    template_name = 'poolstore/poolhouses.html'
    context_object_name = 'poolhouses'


def home(request):

    return render(request, 'poolstore/home.html')

@login_required
def matchup_list(request):
    matchups = Matchup.objects.prefetch_related('messages').select_related('player_accepting').select_related('player_inviting').filter(
    Q(player_inviting=request.user.player) | Q(player_accepting=request.user.player)
    ).annotate(latest_message_time=Max('messages__time_sent')).order_by('-latest_message_time')

    return render(request, 'poolstore/matchup-list.html', {'matchups': matchups})