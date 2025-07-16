#!/usr/bin/env python3
"""
Travel Matrix Visualizer
Generates a visual representation of the travel time matrix from tour results.
"""

import json
import sys
from typing import List, Dict, Any

def load_tour_results(filename: str = "tour_results.json") -> Dict[str, Any]:
    """Load tour results from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found. Run the tour planner first!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {filename}")
        sys.exit(1)

def print_matrix_table(places: List[Dict[str, Any]], travel_matrix: List[List[Dict[str, Any]]]) -> None:
    """Print a formatted travel time matrix table"""
    print("\n" + "="*80)
    print("📊 TRAVEL TIME MATRIX (Walking Mode)")
    print("="*80)
    
    # Print places list
    print("\n📍 PLACES:")
    for i, place in enumerate(places):
        print(f"  {i}: {place['name']}")
    
    # Print matrix header
    print(f"\n⏱️  TRAVEL TIMES (minutes):")
    print("From\\To", end="")
    for i in range(len(places)):
        print(f"  {i:>6}", end="")
    print()
    print("-" * (8 + len(places) * 8))
    
    # Print matrix rows
    for i, row in enumerate(travel_matrix):
        print(f"  {i:>3}  ", end="")
        for j, element in enumerate(row['elements']):
            if element['status'] == 'OK':
                time_mins = element['duration']['value'] / 60
                if i == j:  # Diagonal (same location)
                    print(f"  {time_mins:>6.1f}", end="")
                elif time_mins < 20:  # Short distance
                    print(f"  {time_mins:>6.1f}", end="")
                elif time_mins < 60:  # Medium distance
                    print(f"  {time_mins:>6.1f}", end="")
                else:  # Long distance
                    print(f"  {time_mins:>6.1f}", end="")
            else:
                print(f"  {'N/A':>6}", end="")
        print()

def analyze_matrix(places: List[Dict[str, Any]], travel_matrix: List[List[Dict[str, Any]]]) -> None:
    """Analyze and print statistics about the travel matrix"""
    times = []
    shortest_time = float('inf')
    longest_time = 0
    shortest_pair = None
    longest_pair = None
    
    for i, row in enumerate(travel_matrix):
        for j, element in enumerate(row['elements']):
            if element['status'] == 'OK' and i != j:  # Skip diagonal
                time_mins = element['duration']['value'] / 60
                times.append(time_mins)
                
                if time_mins < shortest_time:
                    shortest_time = time_mins
                    shortest_pair = (i, j)
                
                if time_mins > longest_time:
                    longest_time = time_mins
                    longest_pair = (i, j)
    
    print(f"\n📈 MATRIX STATISTICS:")
    print(f"  • Shortest walk: {shortest_time:.1f} min ({places[shortest_pair[0]]['name']} → {places[shortest_pair[1]]['name']})")
    print(f"  • Longest walk: {longest_time:.1f} min ({places[longest_pair[0]]['name']} → {places[longest_pair[1]]['name']})")
    print(f"  • Average walk: {sum(times)/len(times):.1f} min")
    print(f"  • Total routes: {len(times)}")

def print_transportation_info(data: Dict[str, Any]) -> None:
    """Print information about transportation mode"""
    print("\n" + "="*80)
    print("🚶‍♂️ TRANSPORTATION MODE")
    print("="*80)
    print("Mode: Walking (Pedestrian)")
    print("• Average speed: ~5 km/h (3 mph)")
    print("• Route type: Sidewalks, pedestrian paths, crosswalks")
    print("• Includes: Traffic light waiting times, pedestrian signals")
    print("• Real-world factors: Accessible pathways, urban navigation")
    
    # Check if optimization was performed
    if 'optimization' in data:
        opt = data['optimization']
        print(f"\n🎯 OPTIMIZATION RESULTS:")
        print(f"• Time limit: {opt['time_limit']} minutes")
        print(f"• Selected places: {len(opt['optimized_route'])}")
        print(f"• Total interest: {opt['total_interest']}")
        print(f"• Total time: {opt['total_time']:.1f} minutes")

def print_algorithm_explanation() -> None:
    """Explain how algorithms use the matrix"""
    print("\n" + "="*80)
    print("🧠 HOW ALGORITHMS USE THIS MATRIX")
    print("="*80)
    print("1. KNAPSACK ALGORITHM:")
    print("   • Uses visit_time from places data")
    print("   • Maximizes interest score within time limit")
    print("   • Doesn't directly use travel matrix")
    
    print("\n2. TSP (Traveling Salesman Problem):")
    print("   • Uses travel matrix to find shortest route")
    print("   • Matrix[i][j] = travel time from place i to place j")
    print("   • Nearest neighbor heuristic chooses next closest unvisited place")
    
    print("\n3. MATRIX READING:")
    print("   • Rows = Starting location (FROM)")
    print("   • Columns = Destination location (TO)")
    print("   • Values = Walking time in minutes")
    print("   • Diagonal = Same location (0 minutes)")

def main():
    """Main function"""
    print("🗺️  TRAVEL MATRIX ANALYZER")
    
    # Load data
    data = load_tour_results()
    places = data.get('places', [])
    travel_matrix = data.get('travel_matrix', [])
    
    if not places or not travel_matrix:
        print("❌ Error: No places or travel matrix found in results")
        sys.exit(1)
    
    # Print analysis
    print_transportation_info(data)
    print_matrix_table(places, travel_matrix)
    analyze_matrix(places, travel_matrix)
    print_algorithm_explanation()
    
    print("\n" + "="*80)
    print("✅ Analysis complete! Check the HTML visualization for a detailed view.")
    print("="*80)

if __name__ == "__main__":
    main()
