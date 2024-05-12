from django.shortcuts import get_object_or_404, render
from .models import Invitation, MatchMake, Matchup, PoolHouse, Message
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Max


@login_required
def all_matchups(request):
    all_matchups = Matchup.objects.filter(
    Q(player_inviting=request.user.player) | Q(player_accepting=request.user.player)
    ).annotate(latest_message_time=Max('messages__time_sent')).order_by('-latest_message_time')

    return render(request, 'poolstore/partials/all-matchups.html', {'matchups': all_matchups})