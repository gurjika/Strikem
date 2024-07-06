from collections import OrderedDict
from datetime import datetime, time, timedelta
from django.utils import timezone

def display_available_reservations(reservations, date=datetime.today().date(), last_reservation_previous=None):

    next_reservations = []
    current_reservations = []
    context = {}

    start_time = datetime.combine(date, time(10, 0, 0))
    close_time = datetime.combine(date, time(3, 0, 0))
    day_end_time = datetime.combine(date, time(0, 0, 0))

    
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
                    dt = datetime.combine(current_reservation.date + timedelta(days=1), time(0, 0, 0))
                    current_reservations.append(current_reservation_datetime)
                    next_reservations.append(dt)
                    

            

        if current_reservation_start_datetime < close_time and not end_stamped:
            end_stamped = True

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

    return context