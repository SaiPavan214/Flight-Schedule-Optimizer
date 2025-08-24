# Flight Schedule Optimization and Cascading Delay Analysis ML Models

This repository contains two advanced machine learning models for analyzing and optimizing flight schedules:

## 1. Schedule Optimization Model (`schedule_optimization_model.py`)

### Purpose

This model helps optimize flight schedules by predicting the impact of schedule changes on delays. It can suggest optimal departure times to minimize delays.

### Key Features

- **Multi-model approach**: Tests Random Forest, Gradient Boosting, and Linear Regression to select the best performing model
- **Comprehensive feature engineering**: Creates features from time patterns, historical delays, and route characteristics
- **Schedule optimization**: Tests various schedule adjustments (-2 to +2 hours, -30 to +30 minutes) to find optimal times
- **Visualization**: Generates detailed plots showing optimization results and delay predictions

### Output Files

- `schedule_optimization_results_{FLIGHT_NUMBER}.csv`: Detailed optimization scenarios for each flight
- `schedule_optimization_analysis_{FLIGHT_NUMBER}.png`: Visualization of optimization results

### Usage

```bash
python schedule_optimization_model.py
```

## 2. Cascading Delay Impact Model (`cascading_delay_impact_model.py`)

### Purpose

This model identifies flights that have the biggest cascading impact on the overall schedule, helping prioritize which flights to monitor and optimize.

### Key Features

- **Network analysis**: Uses graph theory to model delay propagation between flights
- **Centrality measures**: Calculates betweenness, closeness, and eigenvector centrality to identify critical flights
- **Clustering analysis**: Groups flights by delay patterns to identify similar risk profiles
- **Comprehensive impact scoring**: Combines multiple factors to rank flights by cascading impact potential

### Output Files

- `high_impact_flights_analysis.csv`: Detailed analysis of flights with highest cascading impact
- `delay_cluster_analysis.csv`: Flight clustering based on delay patterns
- `cascading_delay_analysis.png`: Comprehensive visualization of network analysis

### Usage

```bash
python cascading_delay_impact_model.py
```

## Installation

1. Install required dependencies:

```bash
pip install -r ml_requirements.txt
```

2. Ensure your `flight_data.csv` file is in the same directory as the scripts.

## Data Requirements

The models expect a CSV file with the following columns:

- `Flight_Number`: Unique flight identifier
- `Date`: Flight date
- `Route`: Origin-Destination route (e.g., "BOM-DEL")
- `STD`: Scheduled departure time
- `ATD`: Actual departure time
- `STA`: Scheduled arrival time
- `ATA`: Actual arrival time
- `STD_DateTime`: Scheduled departure datetime
- `ATD_DateTime`: Actual departure datetime
- `STA_DateTime`: Scheduled arrival datetime
- `ATA_DateTime`: Actual arrival datetime
- `Departure_Delay_Minutes`: Departure delay in minutes
- `Arrival_Delay_Minutes`: Arrival delay in minutes
- `Flight_Duration_Minutes`: Flight duration in minutes
- `Day_of_Week`: Day of week (0-6)
- `Hour_of_Day`: Hour of day (0-23)
- `Weekend`: Boolean indicating if it's a weekend
- `Peak_Time`: Boolean indicating if it's peak time

## Model Capabilities

### Schedule Optimization Model

- **Predicts delay impact** of schedule changes
- **Suggests optimal departure times** to minimize delays
- **Analyzes multiple scenarios** with different time adjustments
- **Provides detailed reports** with improvement metrics

### Cascading Delay Impact Model

- **Identifies critical flights** that cause the most cascading delays
- **Analyzes delay propagation** through the network
- **Ranks flights by impact** using multiple centrality measures
- **Clusters flights** by delay patterns for targeted interventions

## Example Results

### Schedule Optimization Example

```
=== SCHEDULE OPTIMIZATION REPORT FOR FLIGHT AI2509 ===

BEST OPTIMIZATION SCENARIO:
New Schedule Time: 05:30
Hour Adjustment: -1
Minute Adjustment: -30
Predicted Delay: 15.2 minutes
Delay Improvement: 23.8 minutes
```

### Cascading Impact Example

```
TOP 10 FLIGHTS WITH HIGHEST CASCADING IMPACT:
 1. AI2509    | Route: BOM-IXC      | Impact Score:  45.67 | Avg Departure Delay: 38.5 min | Frequency: 7
 2. 6E1185    | Route: BOM-CMB      | Impact Score:  42.31 | Avg Departure Delay: 61.7 min | Frequency: 7
 3. GF57      | Route: BOM-BAH      | Impact Score:  39.89 | Avg Departure Delay: 70.4 min | Frequency: 7
```

## Technical Details

### Algorithms Used

- **Random Forest**: For robust prediction with feature importance
- **Gradient Boosting**: For high-accuracy predictions
- **K-means Clustering**: For grouping similar delay patterns
- **Network Analysis**: For modeling delay propagation

### Feature Engineering

- Time-based features (hour, day, weekend, peak time)
- Historical delay patterns
- Route and flight frequency metrics
- Network centrality measures
- Interaction features

### Model Performance

- Schedule Optimization: Typically achieves R² > 0.7
- Cascading Impact: Uses multiple metrics for comprehensive ranking

## Business Applications

1. **Airline Operations**: Optimize schedules to reduce delays and improve on-time performance
2. **Resource Planning**: Identify critical flights for resource allocation
3. **Risk Management**: Prioritize monitoring of high-impact flights
4. **Capacity Planning**: Understand delay propagation patterns for better scheduling

## Future Enhancements

- Real-time prediction capabilities
- Integration with weather data
- Passenger impact analysis
- Cost-benefit analysis of schedule changes
- API endpoints for integration with existing systems

## Support

For questions or issues, please refer to the code comments or create an issue in the repository.
