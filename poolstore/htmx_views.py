from datetime import datetime, time, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from .models import Invitation, MatchMake, Matchup, PoolHouse, Message, Reservation
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Prefetch
from django.db.models import Max
from collections import OrderedDict

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
    print(reservations)
    context = {}
    next_reservations = []
    current_reservations = []
    
   
    date = datetime.strptime(date, '%Y-%m-%d').date()




    start_time = datetime.combine(date, time(10, 0, 0))
    close_time = datetime.combine(date, time(3, 0, 0))
    day_end_time = datetime.combine(date, time(0, 0, 0))

    dt = datetime.combine(date + timedelta(days=1), time(0, 0, 0))


    previous_day = date - timedelta(days=1)
    last_reservation_previous = Reservation.objects.filter(date=previous_day).order_by('start_time').last()
    if last_reservation_previous:
        last_reservation_previous_dt = last_reservation_previous.real_end_time.astimezone(timezone.get_current_timezone()).replace(tzinfo=None)

        if last_reservation_previous_dt > day_end_time:
            day_end_time = last_reservation_previous_dt


    start_stamped = False
    end_stamped = False


    for index in range(0, len(reservations)):
        current_reservation = reservations[index]
        
        current_reservation_start_datetime = datetime.combine(date, current_reservation.start_time)
        current_reservation_datetime = current_reservation.real_end_time.astimezone(timezone.get_current_timezone()).replace(tzinfo=None)
        if current_reservation_start_datetime > start_time and not start_stamped:
            start_stamped = True

            if current_reservation_start_datetime - start_time >= timedelta(minutes=30):
                current_reservations.append(start_time)
                next_reservations.append(current_reservation_start_datetime)

                try:
                    next_res = reservations[index + 1]

                except IndexError:
                    current_reservations.append(current_reservation_datetime)
                    next_reservations.append(dt)
                    

                


        if current_reservation_start_datetime < close_time and not end_stamped:
            end_stamped = True
            print(current_reservation_start_datetime)

            print(day_end_time)
            if current_reservation_start_datetime - day_end_time >= timedelta(minutes=30):
                current_reservations.append(day_end_time)
                next_reservations.append(current_reservation_start_datetime)

                try:
                    next_res = reservations[index + 1]
                    next_res_datetime =datetime.combine(next_res.date, next_res.start_time)
                    if next_res_datetime > close_time:
                        current_reservations.append(current_reservation_datetime)
                        next_reservations.append(close_time)

                except IndexError:
                    current_reservations.append(current_reservation_datetime)
                    next_reservations.append(close_time)

                


        current_reservations.append(current_reservation_datetime)
        
            

        try:
            next_reservation = reservations[index + 1]
            next_reservation_datetime = datetime.combine(next_reservation.date, next_reservation.start_time)
            next_reservations.append(next_reservation_datetime)

            if next_reservation_datetime - current_reservation_datetime < timedelta(minutes=30):
                next_reservations.remove(next_reservation_datetime)
                current_reservations.remove(current_reservation_datetime)

            if current_reservation_datetime < close_time and next_reservation_datetime > close_time:
                next_reservations.remove(next_reservation_datetime)
                current_reservations.remove(current_reservation_datetime)
                if close_time - current_reservation_datetime >= timedelta(minutes=30):
                    next_reservations.append(close_time)
                    current_reservations.append(current_reservation_datetime)


                
        except IndexError:
            dt = datetime.combine(current_reservation.date + timedelta(days=1), time(0, 0, 0))
            if current_reservation_datetime > start_time:
                if dt - current_reservation_datetime >= timedelta(minutes=30):
                    next_reservations.append(dt)
                    break
                current_reservations.remove(current_reservation_datetime)

            else:
                if not close_time - current_reservation_datetime >= timedelta(minutes=30):
                    current_reservations.remove(current_reservation_datetime)
                    break
                next_reservations.append(close_time)


    current_reservations = list(OrderedDict.fromkeys(current_reservations))
    next_reservations = list(OrderedDict.fromkeys(next_reservations))
    reservations_with_next = zip(current_reservations, next_reservations)
    context['reservations_with_next'] = reservations_with_next


    return render(request, 'poolstore/partials/reservations.html', context)