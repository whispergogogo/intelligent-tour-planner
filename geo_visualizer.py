#!/usr/bin/env python3
"""
Simple Geographic Visualization
Shows the relative positions of places and their connections.
"""

import json
import math

def load_and_visualize():
    """Load tour results and create a simple ASCII map"""
    
    with open('tour_results.json', 'r') as f:
        data = json.load(f)
    
    places = data['places']
    travel_matrix = data['travel_matrix']
    
    print("🗺️  GEOGRAPHIC LAYOUT OF PLACES")
    print("="*60)
    
    # Get lat/lng bounds
    lats = [place['location']['lat'] for place in places]
    lngs = [place['location']['lng'] for place in places]
    
    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)
    
    print(f"📍 COORDINATES RANGE:")
    print(f"  Latitude:  {min_lat:.4f} to {max_lat:.4f}")
    print(f"  Longitude: {min_lng:.4f} to {max_lng:.4f}")
    print(f"  Coverage: ~{(max_lat-min_lat)*111:.1f} km N-S, ~{(max_lng-min_lng)*111*math.cos(math.radians((min_lat+max_lat)/2)):.1f} km E-W")
    
    print(f"\n📊 PLACES BY LOCATION (North to South):")
    places_with_idx = [(i, place) for i, place in enumerate(places)]
    places_with_idx.sort(key=lambda x: x[1]['location']['lat'], reverse=True)
    
    for i, (idx, place) in enumerate(places_with_idx):
        lat, lng = place['location']['lat'], place['location']['lng']
        print(f"  {idx}: {place['name'][:30]:<30} ({lat:.4f}, {lng:.4f})")
    
    print(f"\n🔗 SHORTEST CONNECTIONS:")
    # Find shortest connections
    shortest_times = []
    for i, row in enumerate(travel_matrix):
        for j, element in enumerate(row['elements']):
            if element['status'] == 'OK' and i != j:
                time_mins = element['duration']['value'] / 60
                shortest_times.append((time_mins, i, j))
    
    shortest_times.sort()
    for time_mins, i, j in shortest_times[:5]:
        print(f"  {places[i]['name'][:25]:<25} ↔ {places[j]['name'][:25]:<25} : {time_mins:>5.1f} min")
    
    print(f"\n🚶‍♂️ WALKING CLUSTERS (places within 15 minutes):")
    clusters = {}
    for i, row in enumerate(travel_matrix):
        close_places = []
        for j, element in enumerate(row['elements']):
            if element['status'] == 'OK' and i != j:
                time_mins = element['duration']['value'] / 60
                if time_mins <= 15:
                    close_places.append((j, time_mins))
        if close_places:
            clusters[i] = close_places
    
    for i, close_places in clusters.items():
        print(f"  {i}: {places[i]['name'][:20]:<20} → ", end="")
        for j, time_mins in close_places:
            print(f"{j}({time_mins:.1f}min) ", end="")
        print()

if __name__ == "__main__":
    load_and_visualize()
