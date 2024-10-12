import os
import requests

def get_nearby_poolhouses(lat, long, poolhouses):
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    # Construct Google Maps Distance Matrix API URL
    venue_locations = '|'.join([f"{venue.latitude},{venue.longitude}" for venue in poolhouses])
    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?"
        f"origins={lat},{long}&destinations={venue_locations}&key={GOOGLE_MAPS_API_KEY}"
    )
    
    # Make the request to Google Maps
    response = requests.get(url)
    data = response.json()

    # Parse the distances and filter venues within a 5 km radius
    nearby_venues = []
    for i, venue in enumerate(poolhouses):
        distance_in_meters = data['rows'][0]['elements'][i]['distance']['value']
        if distance_in_meters <= 5000:  # 5 km in meters
            nearby_venues.append(venue)

    # Serialize the nearby venues

    return nearby_venues