import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import networkx as nx
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class CascadingDelayAnalyzer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.network_graph = None
        self.impact_scores = {}
        
    def load_and_preprocess_data(self, file_path):
        """Load and preprocess flight data for cascading delay analysis"""
        print("Loading flight data for cascading delay analysis...")
        df = pd.read_csv(file_path)
        
        # Convert datetime columns
        datetime_columns = ['STD_DateTime', 'ATD_DateTime', 'STA_DateTime', 'ATA_DateTime']
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col])
        
        # Extract additional features
        df['STD_Hour'] = df['STD_DateTime'].dt.hour
        df['STD_Minute'] = df['STD_DateTime'].dt.minute
        df['ATD_Hour'] = df['ATD_DateTime'].dt.hour
        df['ATD_Minute'] = df['ATD_DateTime'].dt.minute
        
        # Create route features
        df[['Origin', 'Destination']] = df['Route'].str.split('-', expand=True)
        
        # Encode categorical variables
        categorical_columns = ['Flight_Number', 'Route', 'Origin', 'Destination']
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Calculate cascading delay features
        df = self.calculate_cascading_features(df)
        
        return df
    
    def calculate_cascading_features(self, df):
        """Calculate features related to cascading delays"""
        print("Calculating cascading delay features...")
        
        # Sort by date and time
        df = df.sort_values(['Date', 'STD_DateTime'])
        
        # Calculate delay propagation metrics
        df['Delay_Propagation_Risk'] = 0.0
        df['Cascading_Impact_Score'] = 0.0
        df['Network_Centrality'] = 0.0
        
        # Group by date to analyze daily patterns
        for date in df['Date'].unique():
            daily_flights = df[df['Date'] == date].copy()
            
            # Calculate delay propagation between consecutive flights
            for i in range(len(daily_flights) - 1):
                current_flight = daily_flights.iloc[i]
                next_flight = daily_flights.iloc[i + 1]
                
                # Check if delays propagate
                if (current_flight['Arrival_Delay_Minutes'] > 0 and 
                    next_flight['Departure_Delay_Minutes'] > 0):
                    
                    # Calculate propagation probability
                    time_gap = (next_flight['STD_DateTime'] - current_flight['ATA_DateTime']).total_seconds() / 60
                    if time_gap < 120:  # Less than 2 hours gap
                        propagation_prob = max(0, 1 - (time_gap / 120))
                        df.loc[next_flight.name, 'Delay_Propagation_Risk'] += propagation_prob
        
        # Calculate flight frequency and connectivity
        flight_frequency = df['Flight_Number'].value_counts()
        route_frequency = df['Route'].value_counts()
        
        df['Flight_Frequency'] = df['Flight_Number'].map(flight_frequency)
        df['Route_Frequency'] = df['Route'].map(route_frequency)
        
        # Calculate average delays by route and time
        route_delays = df.groupby('Route')['Departure_Delay_Minutes'].mean()
        hour_delays = df.groupby('STD_Hour')['Departure_Delay_Minutes'].mean()
        
        df['Route_Avg_Delay'] = df['Route'].map(route_delays)
        df['Hour_Avg_Delay'] = df['STD_Hour'].map(hour_delays)
        
        # Calculate cascading impact score
        df['Cascading_Impact_Score'] = (
            df['Departure_Delay_Minutes'] * 0.3 +
            df['Arrival_Delay_Minutes'] * 0.3 +
            df['Delay_Propagation_Risk'] * 0.2 +
            df['Flight_Frequency'] * 0.1 +
            df['Route_Frequency'] * 0.1
        )
        
        # Calculate network centrality (simplified)
        df['Network_Centrality'] = df['Flight_Frequency'] * df['Route_Frequency'] / 1000
        
        return df
    
    def build_delay_network(self, df):
        """Build a network graph to analyze delay propagation"""
        print("Building delay propagation network...")
        
        G = nx.DiGraph()
        
        # Add nodes (flights)
        for flight in df['Flight_Number'].unique():
            flight_data = df[df['Flight_Number'] == flight]
            avg_delay = flight_data['Departure_Delay_Minutes'].mean()
            G.add_node(flight, avg_delay=avg_delay, frequency=len(flight_data))
        
        # Add edges (delay propagation)
        for date in df['Date'].unique():
            daily_flights = df[df['Date'] == date].sort_values('STD_DateTime')
            
            for i in range(len(daily_flights) - 1):
                current_flight = daily_flights.iloc[i]
                next_flight = daily_flights.iloc[i + 1]
                
                # Check for delay propagation
                if (current_flight['Arrival_Delay_Minutes'] > 0 and 
                    next_flight['Departure_Delay_Minutes'] > 0):
                    
                    time_gap = (next_flight['STD_DateTime'] - current_flight['ATA_DateTime']).total_seconds() / 60
                    if time_gap < 120:  # Less than 2 hours gap
                        weight = max(0, 1 - (time_gap / 120))
                        G.add_edge(current_flight['Flight_Number'], 
                                 next_flight['Flight_Number'], 
                                 weight=weight)
        
        self.network_graph = G
        return G
    
    def calculate_network_metrics(self, df):
        """Calculate network-based impact metrics"""
        print("Calculating network impact metrics...")
        
        if self.network_graph is None:
            self.build_delay_network(df)
        
        # Calculate centrality measures
        betweenness_centrality = nx.betweenness_centrality(self.network_graph)
        closeness_centrality = nx.closeness_centrality(self.network_graph)
        
        # Use degree centrality as a robust alternative to eigenvector centrality
        degree_centrality = nx.degree_centrality(self.network_graph)
        
        # Add centrality scores to dataframe
        df['Betweenness_Centrality'] = df['Flight_Number'].map(betweenness_centrality)
        df['Closeness_Centrality'] = df['Flight_Number'].map(closeness_centrality)
        df['Eigenvector_Centrality'] = df['Flight_Number'].map(degree_centrality)  # Using degree centrality instead
        
        # Fill NaN values
        centrality_columns = ['Betweenness_Centrality', 'Closeness_Centrality', 'Eigenvector_Centrality']
        for col in centrality_columns:
            df[col] = df[col].fillna(0)
        
        return df
    
    def train_cascading_model(self, df):
        """Train model to predict cascading impact"""
        print("Training cascading delay impact model...")
        
        # Calculate network metrics
        df = self.calculate_network_metrics(df)
        
        # Prepare features for cascading impact prediction
        feature_columns = [
            'Departure_Delay_Minutes', 'Arrival_Delay_Minutes',
            'Flight_Duration_Minutes', 'Flight_Frequency', 'Route_Frequency',
            'Delay_Propagation_Risk', 'Route_Avg_Delay', 'Hour_Avg_Delay',
            'Betweenness_Centrality', 'Closeness_Centrality', 'Eigenvector_Centrality',
            'Network_Centrality', 'Peak_Time', 'Weekend'
        ]
        
        # Add encoded categorical features
        for col in ['Flight_Number', 'Route', 'Origin', 'Destination']:
            if f'{col}_encoded' in df.columns:
                feature_columns.append(f'{col}_encoded')
        
        X = df[feature_columns].fillna(0)
        y = df['Cascading_Impact_Score']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"R² Score: {r2:.4f}")
        print(f"Mean Squared Error: {mse:.4f}")
        print(f"Mean Absolute Error: {mae:.4f}")
        
        return X_test_scaled, y_test, y_pred
    
    def identify_high_impact_flights(self, df, top_n=20):
        """Identify flights with the highest cascading impact"""
        print(f"Identifying top {top_n} flights with highest cascading impact...")
        
        # Calculate network metrics if not already done
        if 'Betweenness_Centrality' not in df.columns:
            df = self.calculate_network_metrics(df)
        
        # Calculate comprehensive impact score
        df['Comprehensive_Impact_Score'] = (
            df['Cascading_Impact_Score'] * 0.4 +
            df['Betweenness_Centrality'] * 0.2 +
            df['Closeness_Centrality'] * 0.2 +
            df['Eigenvector_Centrality'] * 0.1 +
            df['Network_Centrality'] * 0.1
        )
        
        # Get top impact flights
        high_impact_flights = df.groupby('Flight_Number').agg({
            'Comprehensive_Impact_Score': 'mean',
            'Cascading_Impact_Score': 'mean',
            'Departure_Delay_Minutes': 'mean',
            'Arrival_Delay_Minutes': 'mean',
            'Flight_Frequency': 'first',
            'Route_Frequency': 'first',
            'Betweenness_Centrality': 'mean',
            'Closeness_Centrality': 'mean',
            'Eigenvector_Centrality': 'mean',
            'Route': 'first'
        }).sort_values('Comprehensive_Impact_Score', ascending=False).head(top_n)
        
        return high_impact_flights
    
    def analyze_delay_clusters(self, df):
        """Analyze delay patterns and identify clusters"""
        print("Analyzing delay clusters...")
        
        # Prepare data for clustering
        cluster_features = [
            'Departure_Delay_Minutes', 'Arrival_Delay_Minutes',
            'Flight_Duration_Minutes', 'Flight_Frequency',
            'Delay_Propagation_Risk', 'Cascading_Impact_Score'
        ]
        
        X_cluster = df[cluster_features].fillna(0)
        X_cluster_scaled = self.scaler.fit_transform(X_cluster)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=4, random_state=42)
        df['Delay_Cluster'] = kmeans.fit_predict(X_cluster_scaled)
        
        # Analyze clusters
        cluster_analysis = df.groupby('Delay_Cluster').agg({
            'Departure_Delay_Minutes': ['mean', 'std'],
            'Arrival_Delay_Minutes': ['mean', 'std'],
            'Cascading_Impact_Score': 'mean',
            'Flight_Number': 'count'
        }).round(2)
        
        return df, cluster_analysis
    
    def generate_cascading_report(self, df, high_impact_flights):
        """Generate comprehensive cascading delay report"""
        print("\n=== CASCADING DELAY IMPACT ANALYSIS REPORT ===")
        
        # Save high impact flights
        output_file = "high_impact_flights_analysis.csv"
        high_impact_flights.to_csv(output_file)
        print(f"\nHigh impact flights analysis saved to: {output_file}")
        
        # Generate summary statistics
        print(f"\nTOP 10 FLIGHTS WITH HIGHEST CASCADING IMPACT:")
        print("=" * 80)
        for i, (flight, data) in enumerate(high_impact_flights.head(10).iterrows(), 1):
            print(f"{i:2d}. {flight:8s} | Route: {data['Route']:12s} | "
                  f"Impact Score: {data['Comprehensive_Impact_Score']:6.2f} | "
                  f"Avg Departure Delay: {data['Departure_Delay_Minutes']:5.1f} min | "
                  f"Frequency: {data['Flight_Frequency']:3d}")
        
        # Analyze delay clusters
        df_with_clusters, cluster_analysis = self.analyze_delay_clusters(df)
        
        print(f"\nDELAY CLUSTER ANALYSIS:")
        print("=" * 50)
        print(cluster_analysis)
        
        # Save cluster analysis
        cluster_file = "delay_cluster_analysis.csv"
        df_with_clusters[['Flight_Number', 'Route', 'Delay_Cluster', 'Cascading_Impact_Score']].to_csv(cluster_file, index=False)
        print(f"\nDelay cluster analysis saved to: {cluster_file}")
        
        # Create visualizations
        self.plot_cascading_analysis(df, high_impact_flights)
        
        return high_impact_flights
    
    def plot_cascading_analysis(self, df, high_impact_flights):
        """Create visualizations for cascading delay analysis"""
        plt.figure(figsize=(20, 15))
        
        # Plot 1: Top impact flights
        plt.subplot(3, 3, 1)
        top_10 = high_impact_flights.head(10)
        plt.barh(range(len(top_10)), top_10['Comprehensive_Impact_Score'])
        plt.yticks(range(len(top_10)), top_10.index)
        plt.title('Top 10 Flights by Cascading Impact')
        plt.xlabel('Comprehensive Impact Score')
        
        # Plot 2: Impact score distribution
        plt.subplot(3, 3, 2)
        plt.hist(df['Cascading_Impact_Score'], bins=30, alpha=0.7, edgecolor='black')
        plt.title('Distribution of Cascading Impact Scores')
        plt.xlabel('Cascading Impact Score')
        plt.ylabel('Frequency')
        
        # Plot 3: Delay vs Impact correlation
        plt.subplot(3, 3, 3)
        plt.scatter(df['Departure_Delay_Minutes'], df['Cascading_Impact_Score'], alpha=0.6)
        plt.title('Departure Delay vs Cascading Impact')
        plt.xlabel('Departure Delay (minutes)')
        plt.ylabel('Cascading Impact Score')
        
        # Plot 4: Network centrality distribution
        plt.subplot(3, 3, 4)
        plt.hist(df['Betweenness_Centrality'], bins=20, alpha=0.7, edgecolor='black')
        plt.title('Distribution of Betweenness Centrality')
        plt.xlabel('Betweenness Centrality')
        plt.ylabel('Frequency')
        
        # Plot 5: Route impact analysis
        plt.subplot(3, 3, 5)
        route_impact = df.groupby('Route')['Cascading_Impact_Score'].mean().sort_values(ascending=False).head(10)
        plt.barh(range(len(route_impact)), route_impact.values)
        plt.yticks(range(len(route_impact)), route_impact.index)
        plt.title('Top 10 Routes by Average Cascading Impact')
        plt.xlabel('Average Cascading Impact Score')
        
        # Plot 6: Hour of day impact
        plt.subplot(3, 3, 6)
        hour_impact = df.groupby('STD_Hour')['Cascading_Impact_Score'].mean()
        plt.plot(hour_impact.index, hour_impact.values, marker='o')
        plt.title('Cascading Impact by Hour of Day')
        plt.xlabel('Hour of Day')
        plt.ylabel('Average Cascading Impact Score')
        plt.grid(True, alpha=0.3)
        
        # Plot 7: Flight frequency vs impact
        plt.subplot(3, 3, 7)
        plt.scatter(df['Flight_Frequency'], df['Cascading_Impact_Score'], alpha=0.6)
        plt.title('Flight Frequency vs Cascading Impact')
        plt.xlabel('Flight Frequency')
        plt.ylabel('Cascading Impact Score')
        
        # Plot 8: Delay propagation risk
        plt.subplot(3, 3, 8)
        plt.hist(df['Delay_Propagation_Risk'], bins=20, alpha=0.7, edgecolor='black')
        plt.title('Distribution of Delay Propagation Risk')
        plt.xlabel('Delay Propagation Risk')
        plt.ylabel('Frequency')
        
        # Plot 9: Network graph visualization (simplified)
        plt.subplot(3, 3, 9)
        if self.network_graph is not None:
            # Create a simplified network visualization
            pos = nx.spring_layout(self.network_graph, k=1, iterations=50)
            node_sizes = [self.network_graph.nodes[node]['avg_delay'] * 10 for node in self.network_graph.nodes()]
            nx.draw(self.network_graph, pos, node_size=node_sizes, node_color='lightblue', 
                   with_labels=False, alpha=0.7)
            plt.title('Delay Propagation Network\n(Node size = Avg Delay)')
        
        plt.tight_layout()
        plt.savefig('cascading_delay_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Cascading delay analysis plots saved to: cascading_delay_analysis.png")

def main():
    # Initialize the analyzer
    analyzer = CascadingDelayAnalyzer()
    
    # Load and preprocess data
    df = analyzer.load_and_preprocess_data('flight_data.csv')
    print(f"Loaded {len(df)} flight records")
    
    # Train the cascading impact model
    X_test, y_test, y_pred = analyzer.train_cascading_model(df)
    
    # Identify high impact flights
    high_impact_flights = analyzer.identify_high_impact_flights(df, top_n=25)
    
    # Generate comprehensive report
    analyzer.generate_cascading_report(df, high_impact_flights)
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("SUMMARY: Cascading delay impact analysis completed successfully!")
    print("The model has identified flights with the highest potential for cascading delays.")
    print("Key outputs generated:")
    print("- high_impact_flights_analysis.csv: Detailed analysis of high-impact flights")
    print("- delay_cluster_analysis.csv: Flight clustering based on delay patterns")
    print("- cascading_delay_analysis.png: Comprehensive visualization of results")

if __name__ == "__main__":
    main()
