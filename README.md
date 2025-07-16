# Tour Planner

A Python application that solves the tour guide path planning problem using dynamic programming algorithms. Given a time limit and places of interest, it finds the optimal subset of locations to visit and the best route between them.

## 🧠 Algorithms Used

- **Knapsack Problem**: Maximizes interest value under time constraints
- **TSP Approximation**: Nearest neighbor heuristic for route optimization
- **Dynamic Programming**: Efficient solution for place selection

## Features

- Search for tourist attractions in any city using Google Places API
- Calculate travel times between all locations using Google Distance Matrix API
- **Knapsack optimization**: Select the best subset of places within time limits
- **TSP route optimization**: Find efficient travel routes between selected places
- Generate interest scores and visit time estimates
- Save results to JSON file with optimization details
- Interactive command-line interface

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google Maps API Key:**
   
   **Option 1: Environment Variable (Recommended)**
   ```bash
   export GOOGLE_MAPS_API_KEY="your_api_key_here"
   ```
   
   **Option 2: Use the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Get a Google Maps API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the following APIs:
     - Places API (Text Search)
     - Distance Matrix API
   - Create credentials (API Key)
   - **Important**: Restrict the API key to only these APIs for security

## Usage

Run the application:
```bash
python main.py
```

The application will prompt you for:
- City name (default: Vancouver)
- Place type (default: tourist_attraction)  
- Maximum number of results (default: 5)
- Time limit in minutes (default: 300)

## Example Output

```
=== Tour Planner ===
Enter city name (default: Vancouver): 
Enter place type (default: tourist_attraction): 
Enter max results (default: 5): 
Enter time limit in minutes (default: 300): 

Fetching tourist_attraction in Vancouver...
Found 5 places!

=== Places Information ===
1. Stanley Park
   Address: Vancouver, BC, Canada
   Rating: 4.6
   Interest Score: 9
   Visit Time: 45 minutes

=== Tour Optimization (Time Limit: 300 minutes) ===
Selected 4 places using knapsack algorithm:
  - Stanley Park (Interest: 9, Time: 45min)
  - Granville Island (Interest: 8, Time: 60min)
  - Gastown (Interest: 7, Time: 30min)
  - Canada Place (Interest: 9, Time: 30min)

=== Optimized Route ===
1. Stanley Park (Visit: 45min)
   → Travel to Canada Place: 53.1min
2. Canada Place (Visit: 30min)
   → Travel to Gastown: 12.5min
3. Gastown (Visit: 30min)
   → Travel to Granville Island: 25.3min
4. Granville Island (Visit: 60min)

Total Interest Score: 33
Total Visit Time: 165min
Total Travel Time: 90.9min
Total Time: 255.9min
```

## Algorithm Details

### Knapsack Problem
- **Input**: Places with interest scores and visit times, time limit
- **Goal**: Maximize total interest within time constraint
- **Method**: Dynamic programming with O(n × W) complexity
- **Output**: Optimal subset of places to visit

### TSP Approximation
- **Input**: Selected places and travel time matrix
- **Goal**: Find shortest route visiting all selected places
- **Method**: Nearest neighbor heuristic
- **Output**: Optimized travel route

## API Rate Limits

Be aware of Google Maps API rate limits:
- Places API: 1000 requests per day (free tier)
- Distance Matrix API: 100 requests per day (free tier)

## File Structure

```
tour-planner/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── setup.sh            # Setup script
├── .env.example        # Example environment file
└── tour_results.json   # Generated results (after running)
```

## Error Handling

The application includes comprehensive error handling for:
- Missing API keys
- Network connection issues
- API errors and rate limits
- Invalid responses
- File I/O errors

## Security Notes

- ⚠️ **Never commit API keys to version control**
- Use environment variables for API keys in production
- Restrict API keys to only necessary Google APIs
- Consider implementing API key rotation for high-usage applications

## Academic Context

This project demonstrates:
- **Dynamic Programming**: Knapsack algorithm for optimization
- **Graph Algorithms**: TSP approximation for route planning
- **API Integration**: Real-world data from Google Maps
- **Algorithm Analysis**: Time/space complexity considerations 