import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class FlightScheduleOptimizer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        
    def load_and_preprocess_data(self, file_path):
        """Load and preprocess flight data"""
        print("Loading flight data...")
        df = pd.read_csv(file_path)
        
        # Convert datetime columns
        datetime_columns = ['STD_DateTime', 'ATD_DateTime', 'STA_DateTime', 'ATA_DateTime']
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col])
        
        # Extract additional features
        df['STD_Hour'] = df['STD_DateTime'].dt.hour
        df['STD_Minute'] = df['STD_DateTime'].dt.minute
        df['STD_Day'] = df['STD_DateTime'].dt.day
        df['STD_Month'] = df['STD_DateTime'].dt.month
        
        # Create route features
        df[['Origin', 'Destination']] = df['Route'].str.split('-', expand=True)
        
        # Encode categorical variables
        categorical_columns = ['Flight_Number', 'Route', 'Origin', 'Destination']
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        # Create interaction features
        df['Peak_Weekend'] = df['Peak_Time'].astype(int) * df['Weekend'].astype(int)
        df['Hour_Peak'] = df['Hour_of_Day'] * df['Peak_Time'].astype(int)
        
        # Calculate historical delay patterns
        df['Avg_Departure_Delay'] = df.groupby('Flight_Number')['Departure_Delay_Minutes'].transform('mean')
        df['Avg_Arrival_Delay'] = df.groupby('Flight_Number')['Arrival_Delay_Minutes'].transform('mean')
        df['Delay_Volatility'] = df.groupby('Flight_Number')['Departure_Delay_Minutes'].transform('std')
        
        # Create target variables for optimization
        df['Total_Delay'] = df['Departure_Delay_Minutes'] + df['Arrival_Delay_Minutes']
        df['Delay_Impact_Score'] = (df['Departure_Delay_Minutes'] * 0.4 + 
                                   df['Arrival_Delay_Minutes'] * 0.6) * df['Flight_Duration_Minutes'] / 100
        
        return df
    
    def prepare_features(self, df):
        """Prepare feature columns for modeling"""
        feature_columns = [
            'STD_Hour', 'STD_Minute', 'STD_Day', 'STD_Month',
            'Day_of_Week', 'Hour_of_Day', 'Weekend', 'Peak_Time',
            'Flight_Duration_Minutes', 'Peak_Weekend', 'Hour_Peak',
            'Avg_Departure_Delay', 'Avg_Arrival_Delay', 'Delay_Volatility'
        ]
        
        # Add encoded categorical features
        for col in ['Flight_Number', 'Route', 'Origin', 'Destination']:
            if f'{col}_encoded' in df.columns:
                feature_columns.append(f'{col}_encoded')
        
        self.feature_columns = feature_columns
        return feature_columns
    
    def train_model(self, df, target='Total_Delay'):
        """Train the optimization model"""
        print("Training schedule optimization model...")
        
        # Prepare features
        feature_columns = self.prepare_features(df)
        X = df[feature_columns].fillna(0)
        y = df[target]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train multiple models and select the best
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'Linear Regression': LinearRegression()
        }
        
        best_score = -np.inf
        best_model = None
        
        for name, model in models.items():
            print(f"Training {name}...")
            model.fit(X_train_scaled, y_train)
            score = model.score(X_test_scaled, y_test)
            print(f"{name} R² Score: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_model = model
        
        self.model = best_model
        print(f"\nBest model selected with R² Score: {best_score:.4f}")
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"Mean Squared Error: {mse:.2f}")
        print(f"Mean Absolute Error: {mae:.2f}")
        
        return X_test_scaled, y_test, y_pred
    
    def optimize_schedule(self, df, flight_number, new_std_hour, new_std_minute):
        """Optimize schedule for a specific flight"""
        print(f"\nOptimizing schedule for flight {flight_number}...")
        
        # Get flight data
        flight_data = df[df['Flight_Number'] == flight_number].copy()
        if flight_data.empty:
            print(f"Flight {flight_number} not found in dataset")
            return None
        
        # Create optimization scenarios
        scenarios = []
        original_delay = flight_data['Total_Delay'].mean()
        
        # Test different schedule adjustments
        for hour_adjust in range(-2, 3):  # -2 to +2 hours
            for minute_adjust in range(-30, 31, 15):  # -30 to +30 minutes in 15-min intervals
                new_hour = new_std_hour + hour_adjust
                new_minute = new_std_minute + minute_adjust
                
                if 0 <= new_hour <= 23 and 0 <= new_minute <= 59:
                    # Create modified flight data
                    modified_data = flight_data.copy()
                    modified_data['STD_Hour'] = new_hour
                    modified_data['STD_Minute'] = new_minute
                    
                    # Update derived features
                    modified_data['Hour_of_Day'] = new_hour
                    modified_data['Peak_Time'] = (6 <= new_hour <= 9) | (17 <= new_hour <= 20)
                    modified_data['Peak_Weekend'] = modified_data['Peak_Time'].astype(int) * modified_data['Weekend'].astype(int)
                    modified_data['Hour_Peak'] = new_hour * modified_data['Peak_Time'].astype(int)
                    
                    # Prepare features for prediction
                    feature_columns = self.prepare_features(modified_data)
                    X_modified = modified_data[feature_columns].fillna(0)
                    X_modified_scaled = self.scaler.transform(X_modified)
                    
                    # Predict new delay
                    predicted_delay = self.model.predict(X_modified_scaled).mean()
                    
                    scenarios.append({
                        'Hour_Adjustment': hour_adjust,
                        'Minute_Adjustment': minute_adjust,
                        'New_STD_Hour': new_hour,
                        'New_STD_Minute': new_minute,
                        'Predicted_Delay': predicted_delay,
                        'Delay_Improvement': original_delay - predicted_delay,
                        'New_STD_Time': f"{new_hour:02d}:{new_minute:02d}"
                    })
        
        return pd.DataFrame(scenarios)
    
    def generate_optimization_report(self, df, optimization_results, flight_number):
        """Generate comprehensive optimization report"""
        print(f"\n=== SCHEDULE OPTIMIZATION REPORT FOR FLIGHT {flight_number} ===")
        
        # Find best scenario
        best_scenario = optimization_results.loc[optimization_results['Delay_Improvement'].idxmax()]
        
        print(f"\nBEST OPTIMIZATION SCENARIO:")
        print(f"New Schedule Time: {best_scenario['New_STD_Time']}")
        print(f"Hour Adjustment: {best_scenario['Hour_Adjustment']:+d}")
        print(f"Minute Adjustment: {best_scenario['Minute_Adjustment']:+d}")
        print(f"Predicted Delay: {best_scenario['Predicted_Delay']:.2f} minutes")
        print(f"Delay Improvement: {best_scenario['Delay_Improvement']:.2f} minutes")
        
        # Save detailed results
        output_file = f"schedule_optimization_results_{flight_number}.csv"
        optimization_results.to_csv(output_file, index=False)
        print(f"\nDetailed results saved to: {output_file}")
        
        # Create visualization
        self.plot_optimization_results(optimization_results, flight_number)
        
        return best_scenario
    
    def plot_optimization_results(self, results, flight_number):
        """Plot optimization results"""
        plt.figure(figsize=(15, 10))
        
        # Plot 1: Delay improvement by hour adjustment
        plt.subplot(2, 2, 1)
        hour_improvements = results.groupby('Hour_Adjustment')['Delay_Improvement'].mean()
        plt.bar(hour_improvements.index, hour_improvements.values)
        plt.title(f'Delay Improvement by Hour Adjustment - {flight_number}')
        plt.xlabel('Hour Adjustment')
        plt.ylabel('Average Delay Improvement (minutes)')
        plt.grid(True, alpha=0.3)
        
        # Plot 2: Predicted delay heatmap
        plt.subplot(2, 2, 2)
        pivot_table = results.pivot_table(
            values='Predicted_Delay', 
            index='Hour_Adjustment', 
            columns='Minute_Adjustment', 
            aggfunc='mean'
        )
        sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdYlGn_r')
        plt.title(f'Predicted Delay Heatmap - {flight_number}')
        plt.xlabel('Minute Adjustment')
        plt.ylabel('Hour Adjustment')
        
        # Plot 3: Top 10 best scenarios
        plt.subplot(2, 2, 3)
        top_scenarios = results.nlargest(10, 'Delay_Improvement')
        plt.barh(range(len(top_scenarios)), top_scenarios['Delay_Improvement'])
        plt.yticks(range(len(top_scenarios)), [f"{row['New_STD_Time']}" for _, row in top_scenarios.iterrows()])
        plt.title(f'Top 10 Best Schedule Adjustments - {flight_number}')
        plt.xlabel('Delay Improvement (minutes)')
        
        # Plot 4: Distribution of predicted delays
        plt.subplot(2, 2, 4)
        plt.hist(results['Predicted_Delay'], bins=20, alpha=0.7, edgecolor='black')
        plt.axvline(results['Predicted_Delay'].mean(), color='red', linestyle='--', label='Mean')
        plt.title(f'Distribution of Predicted Delays - {flight_number}')
        plt.xlabel('Predicted Delay (minutes)')
        plt.ylabel('Frequency')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(f'schedule_optimization_analysis_{flight_number}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Optimization analysis plots saved to: schedule_optimization_analysis_{flight_number}.png")

def main():
    # Initialize the optimizer
    optimizer = FlightScheduleOptimizer()
    
    # Load and preprocess data
    df = optimizer.load_and_preprocess_data('flight_data.csv')
    print(f"Loaded {len(df)} flight records")
    
    # Train the model
    X_test, y_test, y_pred = optimizer.train_model(df)
    
    # Test optimization for a few flights
    test_flights = ['AI2509', '6E762', 'GF57']
    
    for flight in test_flights:
        if flight in df['Flight_Number'].values:
            # Get current schedule time
            flight_data = df[df['Flight_Number'] == flight].iloc[0]
            current_hour = flight_data['STD_Hour']
            current_minute = flight_data['STD_Minute']
            
            print(f"\n{'='*60}")
            print(f"Current schedule for {flight}: {current_hour:02d}:{current_minute:02d}")
            
            # Optimize schedule
            optimization_results = optimizer.optimize_schedule(df, flight, current_hour, current_minute)
            
            if optimization_results is not None:
                optimizer.generate_optimization_report(df, optimization_results, flight)
    
    # Generate summary report
    print(f"\n{'='*60}")
    print("SUMMARY: Schedule optimization model training completed successfully!")
    print("The model can now be used to optimize flight schedules and predict delay impacts.")

if __name__ == "__main__":
    main()
