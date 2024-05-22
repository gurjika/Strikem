from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render
from poolstore.views import CLOSING_TIME_TZ_TBILISI
from .models import Invitation, MatchMake, Matchup, PoolHouse, Message, Reservation
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

@login_required
def reservations(request):
    date = request.GET.get('date')
    reservations = Reservation.objects.filter(date=date).order_by('start_time').all()
    context = {}
    next_reservations = []
    current_reservations = []
    current_reservations.append(CLOSING_TIME_TZ_TBILISI, current_reservation)

    for index in range(0, len(reservations)):
        current_reservation = reservations[index]
        current_reservations.append(current_reservation)
        try:
            next_reservation = reservations[index + 1]
            next_reservations.append(next_reservation)

            next_reservation_datetime = datetime.combine(next_reservation.date, next_reservation.start_time)
            current_reservation_datetime = datetime.combine(current_reservation.date, current_reservation.real_end_time)


            if next_reservation_datetime - current_reservation_datetime < timedelta(minutes=30):
                next_reservations.remove(next_reservation)
                current_reservations.remove(current_reservation)
        except IndexError:
            next_reservations.append(CLOSING_TIME_TZ_TBILISI)
    
    reservations_with_next = zip(current_reservations, next_reservations)
    context['reservations_with_next'] = reservations_with_next
    return render(request, 'poolstore/partials/reservations.html', context)