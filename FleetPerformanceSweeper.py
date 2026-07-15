import pandas as pd
import numpy as np
# Note: In your local environment, ensure you run: pip install matplotlib seaborn pandas

class FleetPerformanceSweeper:
    def __init__(self):
        # Truck Profiles
        self.truck_profiles = {
            'Peterbilt 579': {'hp': 455, 'cda': 47.8, 'engine': 'PACCAR MX-13'},
            'Volvo VNL860': {'hp': 455, 'cda': 43.8, 'engine': 'Volvo D13TC'},
            'Kenworth T680': {'hp': 500, 'cda': 46.3, 'engine': 'Cummins X15'}
        }
        self.drivetrain_efficiency = 0.95
        self.rolling_resistance_coef = 0.0062
        self.fuel_density_lbs_gal = 7.1

    def run_single_iteration(self, body, gear_label, weight):
        specs = self.truck_profiles[body]
        hp = specs['hp']
        cda = specs['cda']
        
        # Axle allocation matrix
        if gear_label == 'Most Fuel Efficient':
            axle = 2.15 if body == 'Volvo VNL860' else 2.47
        elif gear_label == 'Most Common Long Haul':
            axle = 2.47 if body == 'Volvo VNL860' else 2.64
        else: # Most Common Mixed-use
            axle = 2.85 if body == 'Volvo VNL860' else 3.08

        # Core physics calculations
        v_6pct = (hp * 375 * self.drivetrain_efficiency) / (weight * (0.06 + self.rolling_resistance_coef))
        total_force_at_50 = (hp * 375 * self.drivetrain_efficiency) / 50.0
        max_grade_at_50 = (total_force_at_50 / weight) - self.rolling_resistance_coef
        
        # Kinematics calculations
        base_accel = 32.0 * (weight / 45000.0)
        if axle > 2.8: base_accel *= 0.9
        elif axle < 2.3: base_accel *= 1.15
        if hp > 475: base_accel *= 0.92
            
        base_pass = 11.0 * (weight / 45000.0)
        if axle < 2.5: base_pass *= 0.92
        elif axle > 2.9: base_pass *= 1.1

        # Internal BSFC fuel calculation method
        def get_mpg(speed, terrain_rolling_factor):
            hp_req = (0.00256 * cda * (speed**3) + weight * self.rolling_resistance_coef * speed) / (375.0 * self.drivetrain_efficiency)
            hp_req += (weight * terrain_rolling_factor * speed) / (375.0 * self.drivetrain_efficiency)
            
            bsfc = 0.285 if axle < 2.5 else 0.310
            if speed == 75: bsfc += 0.030
            elif speed == 55: bsfc -= 0.005
                
            gph = (hp_req * bsfc) / self.fuel_density_lbs_gal
            return round(speed / gph, 2)

        # Flattend dictionary mapping for flawless graphing transitions
        return {
            'Truck_Body': body,
            'Gear_Spec': gear_label,
            'Axle_Ratio': axle,
            'Weight_lbs': int(weight),
            'Accel_0_50_s': round(base_accel, 1),
            'Pass_45_65_s': round(base_pass, 1),
            'Max_Speed_6pct_Grade_MPH': round(v_6pct, 1),
            'Max_Grade_at_50MPH_pct': round(max_grade_at_50 * 100, 2),
            'MPG_I95_55MPH': get_mpg(55, 0.0),
            'MPG_I95_65MPH': get_mpg(65, 0.0),
            'MPG_I95_75MPH': get_mpg(75, 0.0),
            'MPG_I40_55MPH': get_mpg(55, 0.005),
            'MPG_I40_65MPH': get_mpg(65, 0.005),
            'MPG_I40_75MPH': get_mpg(75, 0.005)
        }

    def generate_full_fleet_dataset(self):
        bodies = ['Peterbilt 579', 'Volvo VNL860', 'Kenworth T680']
        gears = ['Most Fuel Efficient', 'Most Common Long Haul', 'Most Common Mixed-use']
        weights = [45000, 50000, 55000, 60000]
        
        all_results = []
        
        # Comprehensive automated parameter sweep
        for b in bodies:
            for g in gears:
                for w in weights:
                    run_data = self.run_single_iteration(b, g, w)
                    all_results.append(run_data)
                    
        # Instantly converts the flat dictionary list into an enterprise dataset table
        return pd.DataFrame(all_results)

# --- Execution of Dataset Generation ---
sweeper = FleetPerformanceSweeper()
df = sweeper.generate_full_fleet_dataset()

# Print the top 5 rows to verify the clean data architecture
print(df.head())

# Optional: Save the dataset to a CSV for further analysis or visualization
df.to_csv('fleet_performance_dataset.csv', index=False)

# Some data plotting examples
import matplotlib.pyplot as plt
import seaborn as sns

# Filters the data to isolate a single standardized weight group
filtered_df = df[df['Weight_lbs'] == 55000]

# Plots a direct comparison of Mountain Speed vs I-95 Cruising Efficiency
sns.scatterplot(data=filtered_df, x='Max_Speed_6pct_Grade_MPH', y='MPG_I95_65MPH', hue='Truck_Body', style='Gear_Spec', s=100)
plt.title("Mountain Performance vs. Highway Efficiency (at 55,000 lbs)")
plt.show()



# Plots the exact degradation curve of passing performance as trucks get heavier
sns.lineplot(data=df, x='Weight_lbs', y='Pass_45_65_s', hue='Gear_Spec', style='Truck_Body', marker='o')
plt.title("Passing Time Degradation Across Weight Increments")
plt.show()


# To enable Excel exports in your local environment, first run:
# pip install pandas openpyxl

import pandas as pd

# Assume 'df' is the complete master DataFrame generated by our FleetPerformanceSweeper class
# Let's create an elegant, multi-tab Excel workbook tailored for executive review

with pd.ExcelWriter('Fleet_Performance_Analysis.xlsx', engine='openpyxl') as writer:
    
    # --- Tab 1: The Master Dataset ---
    # Drops the raw, unfiltered data for data analysts or deep-dives
    df.to_excel(writer, sheet_name='Master Data', index=False)
    
    # --- Tab 2: The Executive Fuel Slasher Review (65 MPH Cruise) ---
    # Filters specifically for the standard 55,000 lb configuration at the standard cruising speed
    exec_summary = df[df['Weight_lbs'] == 55000][[
        'Truck_Body', 'Gear_Spec', 'Axle_Ratio', 
        'MPG_I95_65MPH', 'MPG_I40_65MPH', 
        'Max_Speed_6pct_Grade_MPH', 'Max_Grade_at_50MPH_pct'
    ]]
    exec_summary.to_excel(writer, sheet_name='Executive Summary', index=False)
    
    # --- Tab 3: Weight Sensitivity Matrix ---
    # Groups data by body and weight to show how performance degrades as loads get heavier
    weight_pivot = df.pivot_table(
        index=['Truck_Body', 'Gear_Spec'], 
        columns='Weight_lbs', 
        values=['MPG_I95_65MPH', 'Max_Speed_6pct_Grade_MPH']
    )
    weight_pivot.to_excel(writer, sheet_name='Weight Sensitivity')

print("Excel workbook 'Fleet_Performance_Analysis.xlsx' successfully created with 3 distinct tabs!")



