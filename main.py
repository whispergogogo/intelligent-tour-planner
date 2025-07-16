import requests
import os
from typing import List, Dict, Any, Tuple
import json
import itertools
from dataclasses import dataclass

# Load API key from environment variable for security
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not API_KEY:
    print("Error: Please set the GOOGLE_MAPS_API_KEY environment variable")
    print("You can set it by running: export GOOGLE_MAPS_API_KEY='your_api_key_here'")
    exit(1)

def get_places(city: str = "Vancouver", place_type: str = "tourist_attraction", max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch places from Google Places API
    
    Args:
        city: City to search in
        place_type: Type of place to search for
        max_results: Maximum number of results to return
    
    Returns:
        List of place dictionaries
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{place_type} in {city}",
        "key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            print(f"API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
            return []
        
        places = []
        for result in data.get("results", [])[:max_results]:
            places.append({
                "name": result["name"],
                "address": result["formatted_address"],
                "location": result["geometry"]["location"],
                "rating": result.get("rating", 0),
                "place_id": result["place_id"]
            })
        return places
        
    except requests.RequestException as e:
        print(f"Error fetching places: {e}")
        return []
    except KeyError as e:
        print(f"Error parsing API response: {e}")
        return []

def get_travel_time_matrix(locations: List[Dict[str, Any]], mode: str = "walking") -> List[List[Dict[str, Any]]]:
    """
    Get travel time matrix between all locations
    
    Args:
        locations: List of location dictionaries
        mode: Travel mode (walking, driving, bicycling)
    
    Returns:
        Matrix of travel times
    """
    if not locations:
        return []
    
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    origins = "|".join([f'{loc["location"]["lat"]},{loc["location"]["lng"]}' for loc in locations])
    destinations = origins  # All-to-all matrix

    params = {
        "origins": origins,
        "destinations": destinations,
        "mode": mode,
        "key": API_KEY
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        matrix = response.json()
        
        if matrix.get("status") != "OK":
            print(f"API Error: {matrix.get('status')} - {matrix.get('error_message', 'Unknown error')}")
            return []
        
        return matrix["rows"]
        
    except requests.RequestException as e:
        print(f"Error fetching travel times: {e}")
        return []
    except KeyError as e:
        print(f"Error parsing travel time response: {e}")
        return []

def calculate_place_metrics(places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calculate interest and visit time for each place
    
    Args:
        places: List of place dictionaries
    
    Returns:
        Updated places with interest and visit_time
    """
    for place in places:
        place["interest"] = int(place.get("rating", 0) * 2)
        place["visit_time"] = 30 + (place["interest"] % 3) * 15
    return places

def print_travel_times(places: List[Dict[str, Any]], matrix: List[List[Dict[str, Any]]]) -> None:
    """
    Print travel times between all places
    
    Args:
        places: List of place dictionaries
        matrix: Travel time matrix
    """
    if not matrix or not places:
        print("No travel time data available")
        return
    
    print("\n=== Travel Times (Walking) ===")
    for i, row in enumerate(matrix):
        if i >= len(places):
            break
        for j, element in enumerate(row["elements"]):
            if j >= len(places):
                break
            if element["status"] == "OK":
                time = element["duration"]["value"]  # in seconds
                print(f"Time from {places[i]['name']} to {places[j]['name']} = {time/60:.1f} mins")
            else:
                print(f"Could not calculate time from {places[i]['name']} to {places[j]['name']}")

def print_places_info(places: List[Dict[str, Any]]) -> None:
    """
    Print information about all places (for debugging/reference)
    
    Args:
        places: List of place dictionaries
    """
    print("\n=== Places Information ===")
    for i, place in enumerate(places, 1):
        print(f"{i}. {place['name']}")
        print(f"   Address: {place['address']}")
        print(f"   Rating: {place.get('rating', 'N/A')}")
        print(f"   Interest Score: {place.get('interest', 'N/A')}")
        print(f"   Visit Time: {place.get('visit_time', 'N/A')} minutes")
        print()

def display_places_for_selection(places: List[Dict[str, Any]]) -> None:
    """
    Display places in a formatted table for user selection
    
    Args:
        places: List of place dictionaries
    """
    print(f"\n=== AVAILABLE ATTRACTIONS ===")
    print(f"{'ID':<3} {'Name':<40} {'Rating':<6} {'Interest':<8} {'Visit Time':<10}")
    print("-" * 70)
    
    for i, place in enumerate(places):
        print(f"{i:<3} {place['name'][:39]:<40} {place.get('rating', 'N/A'):<6} {place.get('interest', 'N/A'):<8} {place.get('visit_time', 'N/A')}min")

def get_user_preferences(places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get user preferences for place selection
    
    Args:
        places: List of all available places
    
    Returns:
        List of user-selected places
    """
    print(f"\n=== USER PREFERENCES ===")
    print(f"Found {len(places)} attractions. Please select which ones you're interested in.")
    
    # Display places for selection
    display_places_for_selection(places)
    
    # Get user selection
    print(f"\nPlease select attractions by entering their IDs (comma-separated)")
    print(f"Examples: '0,1,2' or '0, 2, 4, 7' or 'all' for all attractions")
    
    while True:
        try:
            user_input = input("\nYour selection: ").strip()
            
            if user_input.lower() == 'all':
                selected_places = places.copy()
                break
            
            # Parse comma-separated IDs
            selected_ids = [int(id_str.strip()) for id_str in user_input.split(',')]
            
            # Validate IDs
            invalid_ids = [id for id in selected_ids if id < 0 or id >= len(places)]
            if invalid_ids:
                print(f"❌ Invalid IDs: {invalid_ids}. Please use IDs between 0 and {len(places)-1}")
                continue
            
            # Remove duplicates while preserving order
            selected_ids = list(dict.fromkeys(selected_ids))
            selected_places = [places[id] for id in selected_ids]
            break
            
        except ValueError:
            print("❌ Invalid input. Please enter comma-separated numbers or 'all'")
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            return []
    
    # Confirm selection
    print(f"\n✅ You selected {len(selected_places)} attractions:")
    for i, place in enumerate(selected_places, 1):
        print(f"  {i}. {place['name']} (Interest: {place['interest']}, Visit: {place['visit_time']}min)")
    
    # Ask for confirmation
    confirm = input(f"\nProceed with these {len(selected_places)} attractions? (y/n): ").strip().lower()
    if confirm in ['y', 'yes']:
        return selected_places
    else:
        print("Let's try again...")
        return get_user_preferences(places)

def get_additional_preferences() -> Dict[str, Any]:
    """
    Get additional user preferences for tour planning
    
    Returns:
        Dictionary of user preferences
    """
    preferences = {}
    
    print(f"\n=== ADDITIONAL PREFERENCES ===")
    
    # Time limit
    while True:
        try:
            time_input = input("Enter time limit in minutes (default: 300): ").strip()
            preferences['time_limit'] = int(time_input) if time_input else 300
            break
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Starting time (optional)
    while True:
        try:
            start_time = input("Enter starting time (HH:MM format, default: 09:00): ").strip()
            if not start_time:
                preferences['start_time'] = "09:00"
                break
            
            # Validate time format
            time_parts = start_time.split(':')
            if len(time_parts) == 2:
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    preferences['start_time'] = start_time
                    break
            
            print("❌ Invalid time format. Please use HH:MM (e.g., 09:00)")
        except ValueError:
            print("❌ Invalid time format. Please use HH:MM (e.g., 09:00)")
    
    # Priority preference
    print("\nWhat's most important to you?")
    print("1. Maximize number of places visited")
    print("2. Maximize total interest score")
    print("3. Minimize total walking time")
    
    while True:
        try:
            priority = input("Enter your choice (1-3, default: 2): ").strip()
            if not priority:
                preferences['priority'] = 2
                break
            
            priority = int(priority)
            if 1 <= priority <= 3:
                preferences['priority'] = priority
                break
            else:
                print("❌ Please enter 1, 2, or 3")
        except ValueError:
            print("❌ Please enter a valid number")
    
    return preferences

def knapsack_optimization(places: List[Dict[str, Any]], time_limit: int) -> Tuple[List[Dict[str, Any]], int]:
    """
    Solve the knapsack problem to find the best subset of places to visit within time limit
    
    Args:
        places: List of place dictionaries with interest and visit_time
        time_limit: Maximum time available (in minutes)
    
    Returns:
        Tuple of (selected_places, total_interest)
    """
    n = len(places)
    if n == 0:
        return [], 0
    
    # Create DP table
    dp = [[0 for _ in range(time_limit + 1)] for _ in range(n + 1)]
    
    # Fill the DP table
    for i in range(1, n + 1):
        visit_time = places[i-1]['visit_time']
        interest = places[i-1]['interest']
        
        for w in range(time_limit + 1):
            if visit_time <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-visit_time] + interest)
            else:
                dp[i][w] = dp[i-1][w]
    
    # Backtrack to find selected places
    selected_places = []
    w = time_limit
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_places.append(places[i-1])
            w -= places[i-1]['visit_time']
    
    return selected_places, dp[n][time_limit]

def calculate_travel_time(place1: Dict[str, Any], place2: Dict[str, Any], travel_matrix: List[List[Dict[str, Any]]], places: List[Dict[str, Any]]) -> float:
    """
    Calculate travel time between two places using the travel matrix
    
    Args:
        place1: First place dictionary
        place2: Second place dictionary
        travel_matrix: Travel time matrix
        places: List of all places
    
    Returns:
        Travel time in minutes
    """
    try:
        idx1 = places.index(place1)
        idx2 = places.index(place2)
        
        if idx1 < len(travel_matrix) and idx2 < len(travel_matrix[idx1]['elements']):
            element = travel_matrix[idx1]['elements'][idx2]
            if element['status'] == 'OK':
                return element['duration']['value'] / 60  # Convert seconds to minutes
        return float('inf')
    except (ValueError, IndexError, KeyError):
        return float('inf')

def tsp_nearest_neighbor(selected_places: List[Dict[str, Any]], travel_matrix: List[List[Dict[str, Any]]], all_places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Solve TSP using nearest neighbor heuristic
    
    Args:
        selected_places: Places to visit
        travel_matrix: Travel time matrix
        all_places: All places for matrix indexing
    
    Returns:
        Optimized route
    """
    if len(selected_places) <= 1:
        return selected_places
    
    route = [selected_places[0]]  # Start with first place
    unvisited = selected_places[1:]
    
    while unvisited:
        current = route[-1]
        nearest = min(unvisited, key=lambda place: calculate_travel_time(current, place, travel_matrix, all_places))
        route.append(nearest)
        unvisited.remove(nearest)
    
    return route

def generate_detailed_itinerary(optimized_route: List[Dict[str, Any]], travel_matrix: List[List[Dict[str, Any]]], all_places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate detailed itinerary with commute times and schedule
    
    Args:
        optimized_route: Optimized route from TSP
        travel_matrix: Travel time matrix
        all_places: All places for matrix indexing
    
    Returns:
        List of itinerary items with timing details
    """
    itinerary = []
    current_time = 0  # Start at time 0
    
    for i, place in enumerate(optimized_route):
        # Add visit activity
        visit_item = {
            "type": "visit",
            "place": place,
            "start_time": current_time,
            "duration": place['visit_time'],
            "end_time": current_time + place['visit_time'],
            "activity": f"Visit {place['name']}"
        }
        itinerary.append(visit_item)
        current_time += place['visit_time']
        
        # Add travel to next place (if not last place)
        if i < len(optimized_route) - 1:
            next_place = optimized_route[i + 1]
            travel_time = calculate_travel_time(place, next_place, travel_matrix, all_places)
            
            travel_item = {
                "type": "travel",
                "from_place": place,
                "to_place": next_place,
                "start_time": current_time,
                "duration": travel_time,
                "end_time": current_time + travel_time,
                "activity": f"Walk from {place['name']} to {next_place['name']}"
            }
            itinerary.append(travel_item)
            current_time += travel_time
    
    return itinerary

def print_detailed_itinerary(itinerary: List[Dict[str, Any]]) -> None:
    """
    Print detailed itinerary with timeline
    
    Args:
        itinerary: List of itinerary items
    """
    print(f"\n=== DETAILED ITINERARY ===")
    print(f"{'Time':<12} {'Duration':<10} {'Activity':<50}")
    print("-" * 80)
    
    for i, item in enumerate(itinerary, 1):
        start_time = f"{int(item['start_time']//60):02d}:{int(item['start_time']%60):02d}"
        end_time = f"{int(item['end_time']//60):02d}:{int(item['end_time']%60):02d}"
        time_range = f"{start_time}-{end_time}"
        duration = f"{item['duration']:.1f}min"
        
        if item['type'] == 'visit':
            activity = f"🎯 {item['activity']}"
            print(f"{time_range:<12} {duration:<10} {activity:<50}")
            print(f"{'':>12} {'':>10} {'   Interest: ' + str(item['place']['interest']) + '/10, Rating: ' + str(item['place']['rating']):<50}")
        else:  # travel
            activity = f"🚶‍♂️ {item['activity']}"
            print(f"{time_range:<12} {duration:<10} {activity:<50}")
        
        if i < len(itinerary):
            print()

def optimize_tour(places: List[Dict[str, Any]], travel_matrix: List[List[Dict[str, Any]]], time_limit: int) -> Tuple[List[Dict[str, Any]], int, float, List[Dict[str, Any]]]:
    """
    Optimize tour using knapsack + TSP algorithms
    
    Args:
        places: List of all places
        travel_matrix: Travel time matrix
        time_limit: Time limit in minutes
    
    Returns:
        Tuple of (optimized_route, total_interest, total_time, detailed_itinerary)
    """
    print(f"\n=== Tour Optimization (Time Limit: {time_limit} minutes) ===")
    
    # Step 1: Use knapsack to select best places
    selected_places, total_interest = knapsack_optimization(places, time_limit)
    
    if not selected_places:
        print("No places can be visited within the time limit.")
        return [], 0, 0, []
    
    print(f"Selected {len(selected_places)} places using knapsack algorithm:")
    for place in selected_places:
        print(f"  - {place['name']} (Interest: {place['interest']}, Time: {place['visit_time']}min)")
    
    # Step 2: Use TSP to optimize route
    optimized_route = tsp_nearest_neighbor(selected_places, travel_matrix, places)
    
    # Calculate total travel time
    total_travel_time = 0
    total_visit_time = sum(place['visit_time'] for place in optimized_route)
    
    for i in range(len(optimized_route) - 1):
        travel_time = calculate_travel_time(optimized_route[i], optimized_route[i+1], travel_matrix, places)
        total_travel_time += travel_time
    
    total_time = total_visit_time + total_travel_time
    
    print(f"\n=== Optimized Route ===")
    for i, place in enumerate(optimized_route, 1):
        print(f"{i}. {place['name']} (Visit: {place['visit_time']}min)")
        if i < len(optimized_route):
            next_place = optimized_route[i] if i < len(optimized_route) else None
            if next_place:
                travel_time = calculate_travel_time(place, next_place, travel_matrix, places)
                print(f"   → Travel to {next_place['name']}: {travel_time:.1f}min")
    
    print(f"\nTotal Interest Score: {total_interest}")
    print(f"Total Visit Time: {total_visit_time}min")
    print(f"Total Travel Time: {total_travel_time:.1f}min")
    print(f"Total Time: {total_time:.1f}min")
    
    # Generate detailed itinerary
    detailed_itinerary = generate_detailed_itinerary(optimized_route, travel_matrix, places)
    print_detailed_itinerary(detailed_itinerary)
    
    return optimized_route, total_interest, total_time, detailed_itinerary

def generate_detailed_itinerary(optimized_route: List[Dict[str, Any]], travel_matrix: List[List[Dict[str, Any]]], all_places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate a detailed itinerary with commute times and step-by-step instructions
    
    Args:
        optimized_route: Optimized route from TSP
        travel_matrix: Travel time matrix
        all_places: All places for matrix indexing
    
    Returns:
        List of itinerary steps with detailed information
    """
    itinerary = []
    current_time = 0
    
    for i, place in enumerate(optimized_route):
        # Add visit step
        visit_step = {
            "step": i * 2 + 1,
            "type": "visit",
            "place": place,
            "start_time": current_time,
            "duration": place['visit_time'],
            "end_time": current_time + place['visit_time'],
            "description": f"Visit {place['name']}",
            "details": f"Explore {place['name']} for {place['visit_time']} minutes"
        }
        itinerary.append(visit_step)
        current_time += place['visit_time']
        
        # Add travel step (if not last place)
        if i < len(optimized_route) - 1:
            next_place = optimized_route[i + 1]
            travel_time = calculate_travel_time(place, next_place, travel_matrix, all_places)
            
            travel_step = {
                "step": i * 2 + 2,
                "type": "travel",
                "from_place": place,
                "to_place": next_place,
                "start_time": current_time,
                "duration": travel_time,
                "end_time": current_time + travel_time,
                "description": f"Walk from {place['name']} to {next_place['name']}",
                "details": f"Walking time: {travel_time:.1f} minutes"
            }
            itinerary.append(travel_step)
            current_time += travel_time
    
    return itinerary

def print_detailed_itinerary(itinerary: List[Dict[str, Any]]) -> None:
    """
    Print a detailed, time-based itinerary
    
    Args:
        itinerary: List of itinerary steps
    """
    print(f"\n=== DETAILED ITINERARY ===")
    print("=" * 80)
    
    for step in itinerary:
        start_hours = int(step['start_time'] // 60)
        start_mins = int(step['start_time'] % 60)
        end_hours = int(step['end_time'] // 60)
        end_mins = int(step['end_time'] % 60)
        
        if step['type'] == 'visit':
            print(f"🏛️  STEP {step['step']}: {step['description']}")
            print(f"    📍 Location: {step['place']['name']}")
            print(f"    📬 Address: {step['place']['address']}")
            print(f"    ⏰ Time: {start_hours:02d}:{start_mins:02d} - {end_hours:02d}:{end_mins:02d}")
            print(f"    ⏱️  Duration: {step['duration']} minutes")
            print(f"    ⭐ Interest Score: {step['place']['interest']}")
            print(f"    💡 {step['details']}")
        else:  # travel
            print(f"🚶‍♂️ STEP {step['step']}: {step['description']}")
            print(f"    📍 From: {step['from_place']['name']}")
            print(f"    📍 To: {step['to_place']['name']}")
            print(f"    ⏰ Time: {start_hours:02d}:{start_mins:02d} - {end_hours:02d}:{end_mins:02d}")
            print(f"    ⏱️  Duration: {step['duration']:.1f} minutes")
            print(f"    💡 {step['details']}")
        print()

def collect_user_preferences(places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Let user select their preferred places from the available options
    
    Args:
        places: List of all available places
    
    Returns:
        List of user-selected places
    """
    print("\n=== SELECT YOUR PREFERRED ATTRACTIONS ===")
    print("Here are all the attractions we found:")
    print("="*80)
    
    # Display all places with details
    for i, place in enumerate(places, 1):
        print(f"{i:2d}. {place['name']}")
        print(f"    📍 {place['address']}")
        print(f"    ⭐ Rating: {place.get('rating', 'N/A')}")
        print(f"    🎯 Interest Score: {place.get('interest', 'N/A')}")
        print(f"    ⏱️  Estimated Visit Time: {place.get('visit_time', 'N/A')} minutes")
        print()
    
    # Get user selection
    while True:
        try:
            print("📝 How would you like to select your attractions?")
            print("1. Select specific attractions by number")
            print("2. Select all attractions")
            print("3. Select top N attractions by rating")
            
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                return select_specific_attractions(places)
            elif choice == '2':
                print("✅ Selected all attractions!")
                return places
            elif choice == '3':
                return select_top_attractions(places)
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n❌ Selection cancelled.")
            return []

def select_specific_attractions(places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Let user select specific attractions by number
    
    Args:
        places: List of all available places
    
    Returns:
        List of selected places
    """
    while True:
        try:
            selection_input = input(f"\nEnter attraction numbers (1-{len(places)}) separated by commas (e.g., 1,3,5): ").strip()
            
            if not selection_input:
                print("❌ Please enter at least one attraction number.")
                continue
            
            # Parse the selection
            selected_indices = []
            for item in selection_input.split(','):
                try:
                    index = int(item.strip()) - 1  # Convert to 0-based index
                    if 0 <= index < len(places):
                        selected_indices.append(index)
                    else:
                        print(f"❌ Invalid number: {item.strip()}. Please use numbers 1-{len(places)}")
                        raise ValueError()
                except ValueError:
                    print(f"❌ '{item.strip()}' is not a valid number.")
                    raise ValueError()
            
            if not selected_indices:
                print("❌ No valid attractions selected.")
                continue
            
            # Remove duplicates and sort
            selected_indices = sorted(list(set(selected_indices)))
            selected_places = [places[i] for i in selected_indices]
            
            print(f"\n✅ Selected {len(selected_places)} attractions:")
            for i, place in enumerate(selected_places, 1):
                print(f"  {i}. {place['name']}")
            
            return selected_places
            
        except ValueError:
            continue
        except KeyboardInterrupt:
            print("\n❌ Selection cancelled.")
            return []

def select_top_attractions(places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Let user select top N attractions by rating
    
    Args:
        places: List of all available places
    
    Returns:
        List of top-rated places
    """
    while True:
        try:
            n = input(f"\nHow many top attractions would you like to visit? (1-{len(places)}): ").strip()
            n = int(n)
            
            if n <= 0 or n > len(places):
                print(f"❌ Please enter a number between 1 and {len(places)}")
                continue
            
            # Sort by rating (descending) and take top N
            sorted_places = sorted(places, key=lambda x: x.get('rating', 0), reverse=True)
            selected_places = sorted_places[:n]
            
            print(f"\n✅ Selected top {n} attractions by rating:")
            for i, place in enumerate(selected_places, 1):
                print(f"  {i}. {place['name']} (Rating: {place.get('rating', 'N/A')})")
            
            return selected_places
            
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n❌ Selection cancelled.")
            return [], detailed_itinerary

def main():
    """Main function to run the tour planner"""
    print("=== INTELLIGENT TOUR PLANNER ===")
    print("Plan your perfect tour with personalized preferences and detailed itinerary!")
    
    # Get basic input
    city = input("\nEnter city name (default: Vancouver): ").strip() or "Vancouver"
    place_type = input("Enter place type (default: tourist_attraction): ").strip() or "tourist_attraction"
    max_results = input("Enter max results to search (default: 10): ").strip()
    max_results = int(max_results) if max_results.isdigit() else 10
    
    print(f"\nFetching {place_type} in {city}...")
    places = get_places(city, place_type, max_results)
    
    if not places:
        print("No places found. Please check your input and try again.")
        return
    
    print(f"Found {len(places)} places!")
    
    # Calculate metrics
    places = calculate_place_metrics(places)
    
    # Get user preferences for place selection
    selected_places = collect_user_preferences(places)
    
    if not selected_places:
        print("No places selected. Exiting...")
        return
    
    # Get time limit
    time_limit = input("\nEnter time limit in minutes (default: 300): ").strip()
    time_limit = int(time_limit) if time_limit.isdigit() else 300
    
    # Get travel times for selected places only
    print("\nFetching travel times between selected places...")
    matrix = get_travel_time_matrix(selected_places)
    
    # Print travel times
    print_travel_times(selected_places, matrix)
    
    # Optimize tour with user preferences
    optimized_route, total_interest, total_time, detailed_itinerary = optimize_tour(
        selected_places, matrix, time_limit
    )
    
    # Generate summary
    print(f"\n=== TOUR SUMMARY ===")
    print(f"📍 City: {city}")
    print(f"🎯 Place Type: {place_type}")
    print(f"⏰ Time Limit: {time_limit} minutes")
    print(f"🗺️ Selected Places: {len(selected_places)}")
    print(f"📍 Optimized Route: {len(optimized_route)} places")
    print(f"⭐ Total Interest: {total_interest}")
    print(f"⏱️ Total Time: {total_time:.1f} minutes")
    
    # Save results to file
    try:
        results = {
            "city": city,
            "place_type": place_type,
            "time_limit": time_limit,
            "all_places": places,
            "selected_places": selected_places,
            "travel_matrix": matrix,
            "optimization": {
                "time_limit": time_limit,
                "optimized_route": optimized_route,
                "total_interest": total_interest,
                "total_time": total_time,
                "detailed_itinerary": detailed_itinerary
            }
        }
        
        with open("tour_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Complete results saved to tour_results.json")
        print(f"📊 Use 'python3 visualize_matrix.py' to view the travel matrix")
        print(f"🗺️ Use 'python3 geo_visualizer.py' to view geographic layout")
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        
    print(f"\n🎉 Tour planning complete! Enjoy your {city} adventure!")

if __name__ == "__main__":
    main()
