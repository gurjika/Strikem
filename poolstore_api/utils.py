import os
import requests

def get_nearby_poolhouses(lat, long, poolhouses):
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    venue_locations = '|'.join([f"{venue.latitude},{venue.longitude}" for venue in poolhouses])
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?"
        f"origins={lat},{long}&destinations={venue_locations}&key={GOOGLE_MAPS_API_KEY}"
    )
    
    response = requests.get(url)
    data = response.json()

    nearby_venues = []
    for i, venue in enumerate(poolhouses):
        distance_in_meters = data['rows'][0]['elements'][i]['distance']['value']
        if distance_in_meters <= 5000:
            nearby_venues.append(venue)


    return nearby_venues


def check_overlapping_reservations(data, start_time, end_time):

    for res in data:
        if not (start_time >= res.real_end_datetime or end_time <= res.start_time):
            return False
        
    return True