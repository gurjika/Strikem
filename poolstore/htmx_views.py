from datetime import datetime, time, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from .models import Invitation, MatchMake, Matchup, PoolHouse, Message, Reservation
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Prefetch
from django.db.models import Max
from collections import OrderedDict
from .utils import display_available_reservations
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

    # for matchup in all_matchups:
    #     last_messages.append(list(matchup.messages.all())[0])
    
    matchups_with_last_message = zip(last_messages, list(all_matchups))

    context['matchups'] = matchups_with_last_message
    return render(request, 'poolstore/partials/all-matchups.html', context)

@login_required
def reservations(request):
    date = request.GET.get('date')
    reservations = Reservation.objects.filter(date=date).order_by('start_time').all()
    context = {}
    
    
    date = datetime.strptime(date, '%Y-%m-%d').date()
    previous_day = date - timedelta(days=1)
    last_reservation_previous = Reservation.objects.filter(date=previous_day).order_by('start_time').last()

    context = display_available_reservations(reservations, date, last_reservation_previous)


    return render(request, 'poolstore/partials/reservations.html', context)