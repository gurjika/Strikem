from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import get_object_or_404, render
from .models import Invitation, Matchup, Player, PoolHouse, Message, Reservation
from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from collections import OrderedDict
from django.db.models import Q
from django.db.models import Max
from django.http import Http404, HttpResponse
# from .forms import ReservationForm
from django.db.models import Prefetch
from datetime import time
from .utils import display_available_reservations
from django.utils.timezone import make_aware, get_default_timezone
# Create your views here.


def poolhouse(request, poolhouse):
    ph = PoolHouse.objects.get(slug=poolhouse)

    return render(request, 'poolstore/poolhouse.html', {'poolhouse': poolhouse, 'ph': ph})


# @login_required
# def matchmakings(request):
#     matches = MatchMake.objects.all()

#     invites = Invitation.objects.filter(player_invited__user=request.user)

#     context = {
#         'invites': invites,
#         'matches': matches
#     }
    
#     return render(request, 'poolstore/matchmake.html', context)




@login_required
def matchup(request, matchup_id):

    matchup = get_object_or_404(
        Matchup.objects.select_related('player_inviting__user').select_related('player_accepting__user'),
        id=matchup_id
    )


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
               'opponent': opponent
            }
    
    if request.htmx:

        load_type = request.GET.get('load_type')
        if load_type == 'load-matchup':

            return render(request, 'poolstore/partials/matchup_chat.html', context)
        
        return render(request, 'poolstore/partials/matchup-elements.html', context)
    

    all_matchups = Matchup.objects.prefetch_related(
    Prefetch('messages', queryset=Message.objects.all().select_related('sender__user')),
    ).select_related('player_inviting__user', 'player_accepting__user').filter(Q(player_inviting=request.user.player) | Q(player_accepting=request.user.player)
    ).annotate(latest_message_time=Max('messages__time_sent')).order_by('-latest_message_time')

    last_messages = []

    for matchup in all_matchups:
        try:
            last_messages.append(list(matchup.messages.all())[-1])
        except IndexError:
            last_messages.append(None)

    matchups_with_last_message = zip(last_messages, list(all_matchups))

    context['matchups'] = matchups_with_last_message
    return render(request, 'poolstore/matchup.html', context)

    

class PoolHouseListView(ListView):
    template_name = 'poolstore/poolhouses.html'
    context_object_name = 'poolhouses'

    def get_queryset(self):
        return PoolHouse.objects.all()


def home(request):
    return render(request, 'poolstore/home.html')

@login_required
def matchup_list(request):
    all_matchups = Matchup.objects.prefetch_related(
    Prefetch('messages', queryset=Message.objects.all().select_related('sender__user')),
    ).select_related('player_inviting__user', 'player_accepting__user').filter(Q(player_inviting=request.user.player) | Q(player_accepting=request.user.player)
    ).annotate(latest_message_time=Max('messages__time_sent')).order_by('-latest_message_time')

    last_messages = []
    context = {}
    for matchup in all_matchups:
        try:
            last_messages.append(list(matchup.messages.all())[-1])
        except IndexError:
            last_messages.append(None)

    matchups_with_last_message = zip(last_messages, list(all_matchups))

    context['matchups'] = matchups_with_last_message
    return render(request, 'poolstore/matchup-list.html', context)


# class ReservationView(LoginRequiredMixin, CreateView):
#     template_name = 'poolstore/booking.html'
#     form_class = ReservationForm
#     success_url = '/'




#     def form_valid(self, form):
#         start_time = form.instance.start_time
#         reservation_date = form.instance.date
        
#         start_datetime = datetime.combine(reservation_date, start_time)
#         tbilisi_tz = pytz.timezone('Asia/Tbilisi')
#         start_time_tbilisi = tbilisi_tz.localize(start_datetime)

#         start_time_tbilisi_utc = start_time_tbilisi.astimezone(pytz.UTC)

#         reminder_time = start_time_tbilisi_utc - timedelta(minutes=5)

#         notify.apply_async((form.instance.id,), eta=reminder_time)



#         end_datetime = (start_datetime + timedelta(minutes=int(form.instance.duration)))
#         real_end_datetime = end_datetime + timedelta(minutes=5)


#         end_datetime_utc = end_datetime.astimezone(pytz.UTC)
#         real_end_datetime_utc = real_end_datetime.astimezone(pytz.UTC)


#         form.instance.end_time = end_datetime_utc
#         form.instance.real_end_time = real_end_datetime_utc
#         form.instance.table_id = self.kwargs['table_pk']
#         form.instance.player = self.request.user.player


#         return super().form_valid(form)
    

#     # TODO FIX RESERVATION ENDING NEXT DAY

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         reservations = Reservation.objects.filter(date=datetime.today()).order_by('start_time').all()
#         context.update(display_available_reservations(reservations))
        
#         return context
    
# class MyReservationView(LoginRequiredMixin, ListView):
#     template_name = 'poolstore/my-reservations.html'
#     context_object_name = 'reservations'

#     def get_queryset(self) -> QuerySet[Any]:
#         queryset = Reservation.objects.filter(player=self.request.user.player)
#         return queryset