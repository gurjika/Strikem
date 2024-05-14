from django.shortcuts import get_object_or_404, render
from .models import Invitation, MatchMake, Matchup, PoolHouse, Message
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Prefetch

from django.db.models import Max

#NEEEDS FIX. WHOLE PARTIAL RELOAD NOT EFFICIENT
@login_required
def all_matchups(request):
    all_matchups = Matchup.objects.prefetch_related(
    Prefetch('messages', queryset=Message.objects.all().select_related('sender__user')),
        'player_inviting__user',
        'player_accepting__user'
    ).filter(Q(player_inviting=request.user.player) | Q(player_accepting=request.user.player)
    ).annotate(latest_message_time=Max('messages__time_sent')).order_by('-latest_message_time')

    last_messages = []
    context = {}

    for matchup in all_matchups:
        last_messages.append(list(matchup.messages.all())[-1])
    
    matchups_with_last_message = zip(last_messages, list(all_matchups))

    context['matchups'] = matchups_with_last_message
    return render(request, 'poolstore/partials/all-matchups.html', context)