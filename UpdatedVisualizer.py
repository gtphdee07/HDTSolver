import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Ensure local environment has plotting libraries: pip install pandas numpy matplotlib seaborn openpyxl

class FleetDataVisualizer:
    def __init__(self, output_dir="fleet_reports", palette="Set1"):
        """
        Initializes the visualizer, configures global plotting styles, 
        and ensures a target directory exists to compile file outputs safely.
        """
        self.output_dir = output_dir
        self.palette = palette
        
        # Configure clean, executive-level typography and line styling defaults
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({
            'font.size': 11,
            'axes.labelsize': 12,
            'axes.titlesize': 13,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'figure.titlesize': 15,
            'legend.fontsize': 10
        })
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def plot_graph_1_fuel_slasher(self, tidy_df, target_payload=35000):
        """
        Generates the Multi-Speed Fuel Slasher Line Plot (I-95 Flats).
        Isolates a standardized payload to show pure aerodynamic velocity decay curves.
        """
        plt.figure(figsize=(11, 6))
        
        # Filter the long-form dataframe using specific row metrics
        df_flat = tidy_df[
            (tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher') & 
            (tidy_df['Trailer_Payload_lbs'] == target_payload)
        ]
        
        if df_flat.empty:
            print(f"Visualizer Warning: No valid data found for Graph 1 at payload {target_payload} lbs.")
            plt.close()
            return None

        # Render explicit lines for each truck split by its rear axle carrier cut styles
        sns.lineplot(
            data=df_flat, x='Speed_MPH', y='Calculated_MPG', 
            hue='Truck_Model', style='Axle_Ratio', 
            markers=True, dashes=True, linewidth=2.5, palette=self.palette
        )

        plt.title(f'Graph 1: Aerodynamic Speed Penalty Corridor Matrix\n(Flat Highway Cruise at {target_payload:,} lbs Payload)', fontweight='bold', pad=15)
        plt.xlabel('Vehicle Cruising Speed (MPH)', labelpad=10)
        plt.ylabel('Calculated Fuel Efficiency (MPG)', labelpad=10)
        
        # Force exact x-axis locks based on known scenario speeds
        unique_speeds = sorted(df_flat['Speed_MPH'].unique())
        plt.xticks(unique_speeds)
        
        plt.legend(title='Vehicle Config Profiles', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_1_fuel_slasher.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_2_tradeoff_scatter(self, tidy_df):
        """
        Generates the Mountain Climb vs. Flat-Land Economy Scatter Plot.
        Maps the ultimate physical engineering compromises across Quadrants.
        """
        plt.figure(figsize=(11, 6))
        
        # Filter down to look cleanly at standardized 65 MPH cruise baselines
        df_tradeoff = tidy_df[
            (tidy_df['Speed_MPH'] == 65) & 
            (tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher')
        ]

        if df_tradeoff.empty:
            print("Visualizer Warning: No valid data found for Graph 2 Trade-off Scatter.")
            plt.close()
            return None

        # Map scatter plots where bubble size dictates shifting trailer load sizes
        sns.scatterplot(
            data=df_tradeoff, x='Max_Speed_6pct_Grade_MPH', y='Calculated_MPG',
            hue='Truck_Model', style='Axle_Ratio', size='Trailer_Payload_lbs',
            sizes=(50, 250), palette=self.palette, alpha=0.85
        )

        # Draw a custom cross-hair reference grid to block out corporate efficiency quadrants
        plt.axvline(x=38, color='gray', linestyle=':', linewidth=1.5, alpha=0.7)
        plt.axhline(y=8.0, color='gray', linestyle=':', linewidth=1.5, alpha=0.7)

        # Apply structural corporate labels straight onto the plot grid area
        plt.text(26, 9.5, "Quadrant I\n[Fuel Squeezers]", color='darkgreen', fontsize=10, weight='semibold', alpha=0.7)
        plt.text(42, 5.5, "Quadrant II\n[Mountain Tamers]", color='darkblue', fontsize=10, weight='semibold', alpha=0.7)

        plt.title('Graph 2: Fleet Performance Trade-Off Mapping Matrix\n(Mountain Climb Velocity vs. Flat Land Fuel Economy)', fontweight='bold', pad=15)
        plt.xlabel('Maximum Attainable Speed Up a 6% Grade (MPH)', labelpad=10)
        plt.ylabel('Cruising Fuel Efficiency at 65 MPH (MPG)', labelpad=10)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Config & Payload Size')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_2_performance_tradeoff.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_4_braking_safety(self, tidy_df, descent_speed=45):
        """
        Generates the Downhill Descent Control Threshold Bar Plot.
        Maps dynamic brake wear zones as a function of changing trailer loads.
        """
        fig, ax = plt.subplots(figsize=(11, 6))
        
        # Filter down to analyze braking dynamics at the exact descent crawl speed
        df_braking = tidy_df[
            (tidy_df['Speed_MPH'] == descent_speed) & 
            (tidy_df['Route_Scenario'] == 'I70_Mountain_Conqueror')
        ].copy()
        
        df_braking = df_braking.drop_duplicates(subset=['Truck_Model', 'Trailer_Payload_lbs'])

        if df_braking.empty:
            print(f"Visualizer Warning: No valid mountain data found for speed {descent_speed} MPH.")
            plt.close()
            return None

        # Build side-by-side grouped bars for payload weight segments
        sns.barplot(
            data=df_braking, x='Trailer_Payload_lbs', y='Downhill_Req_Braking_HP',
            hue='Truck_Model', palette=self.palette, ax=ax, edgecolor='black', alpha=0.8
        )

        # Apply structural factory-safety horizontal lines matching our mock-up parameters
        ax.axhline(y=250, color='red', linestyle='--', linewidth=2, label='Ford 6.7L HO Exhaust Brake Max (250 HP)')
        ax.axhline(y=450, color='orange', linestyle='-.', linewidth=2, label='Cummins X15 Efficiency Jake Max (450 HP)')
        ax.axhline(y=530, color='darkgreen', linestyle=':', linewidth=2, label='Volvo D13TC Engine Brake Max (530 HP)')

        # Highlight the high-risk friction fade hazard zone via background shading overlay
        ax.axhspan(250, 600, color='red', alpha=0.03, label='Critical Brake Fade Zone (Foot Assist Required)')

        ax.set_title(f'Graph 4: Downhill Compression Brake Safety Limits\n(Continuous Horsepower Demanded to Hold {descent_speed} MPH Down a 6% Grade)', fontweight='bold', pad=15)
        ax.set_xlabel('Trailer Payload Weight (lbs)', labelpad=10)
        ax.set_ylabel('Required Continuous Retarding Power (HP)', labelpad=10)
        ax.set_ylim(0, 600)

        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_4_braking_safety.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

        # =====================================================================
    # WAVE 1 COMPLETION PACK: GRAPHS 3, 5, 6, 7, and 8 (ALIGNED TO NEW KEYS)
    # =====================================================================

    def plot_graph_3_kinematics_bars(self, tidy_df):
        """
        Generates the Grouped Kinematics Responsiveness Bar Chart.
        Visually displays 0-50 launch times and 45-65 passing times 
        as a function of shifting trailer payload weights.
        """
        # Filter down to flat-ground cruising rows to compare pure mechanical acceleration
        df_accel = tidy_df[tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher'].copy()
        if df_accel.empty:
            print("Visualizer Warning: No valid flat-ground data found for Graph 3.")
            return None

        # Reshape (melt) the timing metrics to allow side-by-side grouped plotting
        df_melted = df_accel.melt(
            id_vars=['Truck_Model', 'Trailer_Payload_lbs', 'Axle_Ratio'],
            value_vars=['Accel_0_50_s', 'Passing_45_65_s'],
            var_name='Performance_Metric', value_name='Time_Seconds'
        )

        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        
        # Panel A: 0-50 MPH Launch Times
        sns.barplot(
            data=df_melted[df_melted['Performance_Metric'] == 'Accel_0_50_s'],
            x='Trailer_Payload_lbs', y='Time_Seconds', hue='Truck_Model',
            palette=self.palette, edgecolor='black', alpha=0.8, ax=axes[0]
        )
        axes[0].set_title('A: 0-50 MPH Launch Responsiveness')
        axes[0].set_xlabel('Trailer Payload Weight (lbs)')
        axes[0].set_ylabel('Time in Seconds (Shorter is Better)')
        if axes[0].get_legend(): axes[0].get_legend().remove()

        # Panel B: 45-65 MPH Passing Responsiveness
        sns.barplot(
            data=df_melted[df_melted['Performance_Metric'] == 'Passing_45_65_s'],
            x='Trailer_Payload_lbs', y='Time_Seconds', hue='Truck_Model',
            palette=self.palette, edgecolor='black', alpha=0.8, ax=axes[1]
        )
        axes[1].set_title('B: 45-65 MPH Highway Passing Sprint')
        axes[1].set_xlabel('Trailer Payload Weight (lbs)')
        axes[1].set_ylabel('') # Shared axis
        
        plt.suptitle('Graph 3: Kinematic Performance & Acceleration Timings Scorecard', fontweight='bold', y=0.98)
        plt.legend(title='Vehicle Configuration', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_3_kinematics_bars.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_5_route_cost_split(self, tidy_df, diesel_price_per_gal=4.00, def_price_per_gal=5.00):
        """
        Generates the Operating Cost Split Stacked Bar Chart.
        Converts fuel consumption data into fluid expenses per 1,000 miles.
        """
        # Filter for a standardized 35,000 lb trailer payload at standard 65 MPH cruise speed
        df_cost = tidy_df[(tidy_df['Speed_MPH'] == 65) & (tidy_df['Trailer_Payload_lbs'] == 35000)].copy()
        if df_cost.empty:
            print("Visualizer Warning: Missing 65 MPH cruising data for Graph 5.")
            return None

        # Operational financial logic: Calculate costs per 1,000 miles
        df_cost['Diesel_Cost_Per_1k_Miles'] = (1000 / df_cost['Calculated_MPG']) * diesel_price_per_gal
        
        # Estimate dynamic load-based DEF consumption (typically 3% to 5% of fuel volume)
        df_cost['DEF_Cost_Per_1k_Miles'] = ((1000 / df_cost['Calculated_MPG']) * 0.04) * def_price_per_gal

        # Create a unique configuration string tag for the chart axis label
        df_cost['Config_Label'] = df_cost['Truck_Model'] + " (" + df_cost['Axle_Ratio'].astype(str) + " Axle)"

        plt.figure(figsize=(12, 6))
        
        # Plot stacked elements sequentially by drawing the larger bar, then overlaying the smaller bar
        sns.barplot(data=df_cost, x='Config_Label', y='Diesel_Cost_Per_1k_Miles', color='darkblue', alpha=0.85, label='Diesel Fuel Cost')
        sns.barplot(data=df_cost, x='Config_Label', y='DEF_Cost_Per_1k_Miles', color='cyan', alpha=0.6, label='DEF Fluid Cost', bottom=df_cost['Diesel_Cost_Per_1k_Miles'])

        plt.title('Graph 5: Route Operating Fluid Cost Comparison\n(Projected Expenses Per 1,000 Miles at a Steady 65 MPH)', fontweight='bold', pad=15)
        plt.xlabel('Vehicle Configuration Profile')
        plt.ylabel('Operating Fluid Cost ($ per 1,000 Miles)')
        plt.xticks(rotation=15, ha='right')
        plt.legend(title='Fluid Breakdown', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_5_route_cost_split.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_6_gear_hunting_heatmap(self, tidy_df):
        """
        Generates the Shift Frequency / Gear Hunting Risk Matrix Heatmap.
        Maps expected transmission stability based on shifting payload weights.
        """
        # Isolate the rolling hills route profile where gear hunting actively manifests
        df_hills = tidy_df[tidy_df['Route_Scenario'] == 'I40_Midwest_Rhythm'].copy()
        if df_hills.empty:
            print("Visualizer Warning: Missing rolling terrain entries for Graph 6.")
            return None

        # Build a mathematical proxy for Gear Hunting Risk (Stability Score)
        # Driven by the interaction of engine load % and axle ratio leverage
        df_hills['Gear_Hunting_Risk'] = (df_hills['Engine_Load_Pct'] * 0.1) + (4.30 - df_hills['Axle_Ratio'].astype(float)) * 1.5
        df_hills['Gear_Hunting_Risk'] = df_hills['Gear_Hunting_Risk'].clip(lower=1.0, upper=10.0)

        # Pivot rows into a clean 2D numerical grid map format matching the new key name
        heatmap_data = df_hills.pivot_table(
            index='Axle_Ratio', columns='Trailer_Payload_lbs', 
            values='Gear_Hunting_Risk', aggfunc='mean'
        )

        plt.figure(figsize=(9, 6))
        # Draw a custom sequential heatmap shifting from green (stable) to dark red (unstable)
        sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="RdYlGn_r", cbar_kws={'label': 'Gear Hunting Risk Rating (1=Stable, 10=Severe)'}, linewidths=0.5)

        plt.title('Graph 6: Transmission Stability & Gear Hunting Risk Matrix\n(Continuous Hill Cruising Over Shifting Trailer Payloads)', fontweight='bold', pad=15)
        plt.xlabel('Trailer Payload Weight (lbs)')
        plt.ylabel('Drivetrain Rear End Axle Ratio')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_6_gear_hunting_heatmap.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_7_lugging_risk_RPM(self, tidy_df):
        """
        Generates the Low-RPM Mountain Lugging Safety Boundary Chart.
        Maps the distance to a torque cliff when climbing steep inclines.
        """
        # Filter strictly for mountain climbing performance passes
        df_mountain = tidy_df[tidy_df['Route_Scenario'] == 'I70_Mountain_Conqueror'].copy()
        if df_mountain.empty:
            print("Visualizer Warning: No mountain data found for Graph 7.")
            return None

        plt.figure(figsize=(11, 6))
        
        # Plot continuous line sweeps tracking current engine RPM across vehicle speeds
        sns.lineplot(
            data=df_mountain, x='Speed_MPH', y='Engine_Cruise_RPM', 
            hue='Truck_Model', style='Axle_Ratio', markers=True, linewidth=2.5, palette=self.palette
        )

        # Draw horizontal warning indicators mapping engine family torque sweet spots
        plt.axhline(y=1000, color='red', linestyle='--', linewidth=2, label='Class 8 Torque Drop Threshold (1,000 RPM)')
        plt.axhline(y=1600, color='darkgreen', linestyle=':', linewidth=1.5, label='Ford 6.7L HO Torque Start (1,600 RPM)')

        # Fill the bottom damage risk zone explicitly with a translucent color block
        plt.axhspan(600, 1000, color='red', alpha=0.05, label='Severe Low-End Lugging Zone')

        plt.title('Graph 7: Mountain Climb Engine RPM & Lugging Safety Limits\n(Engine Rotation Tracking Across Forced Road Speeds on a 6% Grade)', fontweight='bold', pad=15)
        plt.xlabel('Forced Climb Vehicle Speed (MPH)')
        plt.ylabel('Engine Rotation Speed (RPM)')
        plt.ylim(500, 2800) # Expands boundary scale to capture Ford light-truck engines
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_7_lugging_risk_boundaries.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_8_speed_penalty_ROI(self, tidy_df):
        """
        Generates the Time Saved vs. Fuel Lost ROI Cross Plot.
        Visualizes the economic point of diminishing financial returns.
        """
        # Filter for standard flat long-haul configurations at standard mid-weight payloads
        df_roi = tidy_df[
            (tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher') & 
            (tidy_df['Trailer_Payload_lbs'] == 35000)
        ].copy()
        
        if df_roi.empty:
            print("Visualizer Warning: Missing data rows for Graph 8.")
            return None

        # Build baseline variables over a 100,000 mile lifecycle using the updated keys
        df_roi['Annual_Windshield_Hours'] = 100000 / df_roi['Speed_MPH']
        df_roi['Annual_Fuel_Bill_Dollars'] = (100000 / df_roi['Calculated_MPG']) * 4.00

        # Group data by tested speed to isolate global fleet averages
        df_grouped = df_roi.groupby('Speed_MPH', as_index=False).mean(numeric_only=True)

        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Y-Axis 1: Plot the Annual Fuel Bill curve in bold red
        color = 'tab:red'
        ax1.set_xlabel('Target Cruising Speed (MPH)', fontsize=12)
        ax1.set_ylabel('Average Annual Fuel Expense ($)', color=color, fontsize=12)
        line1 = ax1.plot(
            df_grouped['Speed_MPH'], 
            df_grouped['Annual_Fuel_Bill_Dollars'], 
            color=color, marker='o', linewidth=3, 
            label='Annual Fuel Bill ($)'
        )
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, linestyle=':', alpha=0.6)

        # Y-Axis 2: Instantly instantiate a twin coordinate layer sharing the same X-axis
        ax2 = ax1.twinx()  
        color = 'tab:blue'
        ax2.set_ylabel('Annual Driver Windshield Hours (Hrs)', color=color, fontsize=12)
        line2 = ax2.plot(
            df_grouped['Speed_MPH'], 
            df_grouped['Annual_Windshield_Hours'], 
            color=color, marker='s', linewidth=3, 
            linestyle='--', label='Windshield Time (Hours)'
        )
        ax2.tick_params(axis='y', labelcolor=color)

        # Merge the distinct dual axes labels into a single integrated visual box legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper center')

        plt.title('Graph 8: Fleet Velocity ROI Return Matrix\n(Annual Fuel Dollars Spent vs. Windshield Hours Saved Over 100,000 Miles)', fontweight='bold', pad=15)
        fig.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_8_speed_penalty_roi.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path




# =====================================================================
# SEAMLESS RUNNER PIPELINE FOR TESTING VISUALIZATIONS LOCALLY
# =====================================================================
# =====================================================================
# SEAMLESS RUNNER PIPELINE FOR TESTING VISUALIZATIONS LOCALLY
# =====================================================================
if __name__ == '__main__':
    # 1. Create a structured DataFrame that perfectly mirrors your core physics pipeline data shape
    print("--- STARTING COGNITIVE DATA VECTORS SWEEP ---")
    mock_records = []
    
    trucks = ['Ford F-450 DRW HO', 'Kenworth T680 X15', 'Volvo VNL 860 D13TC']
    payloads = [25000, 30000, 35000, 40000, 45000]
    speeds_i95 = [55, 65, 75]
    speeds_i70 = [35, 45]

    for t in trucks:
        axles = [4.30] if 'Ford' in t else ([2.15, 2.47, 2.64] if 'Volvo' in t else [2.64, 2.79, 3.08])
        weight_modifier = 8600 if 'Ford' in t else (18900 if 'Volvo' in t else 18400)
        base_mpg = 8.5 if 'Ford' in t else (10.5 if 'Volvo' in t else 9.8)
        
        for ax in axles:
            for p in payloads:
                total_w = weight_modifier + p
                
                # Populates structural parameters for the I-95 Flat Land Cruise
                for sp in speeds_i95:
                    penalty = (sp - 55) * 0.16 if 'Ford' in t else (sp - 55) * 0.22
                    w_penalty = (p - 25000) * 0.00004
                    mpg_calc = max(4.8, base_mpg - penalty - w_penalty)
                    
                    mock_records.append({
                        'Truck_Model': t, 
                        'Axle_Ratio': ax, 
                        'Trailer_Payload_lbs': p,
                        'Route_Scenario': 'I95_Fuel_Slasher', 
                        'Speed_MPH': sp, 
                        'Calculated_MPG': round(mpg_calc, 2),
                        'Max_Speed_6pct_Grade_MPH': round(74.0 - (total_w * 0.0009), 1) if 'Ford' in t else round(64.5 - (total_w * 0.00041), 1),
                        'Downhill_Req_Braking_HP': round(((total_w * 0.06 - total_w * 0.0062) * 45) / 375, 1)
                    })
                
                # Populates parameters for the severe I-70 Mountain Climb
                for sp in speeds_i70:
                    w_penalty = (p - 25000) * 0.00005
                    mpg_calc = max(2.8, (base_mpg * 0.38) - w_penalty)
                    
                    mock_records.append({
                        'Truck_Model': t, 
                        'Axle_Ratio': ax, 
                        'Trailer_Payload_lbs': p,
                        'Route_Scenario': 'I70_Mountain_Conqueror', 
                        'Speed_MPH': sp, 
                        'Calculated_MPG': round(mpg_calc, 2),
                        'Max_Speed_6pct_Grade_MPH': round(74.0 - (total_w * 0.0009), 1) if 'Ford' in t else round(64.5 - (total_w * 0.00041), 1),
                        'Downhill_Req_Braking_HP': round(((total_w * 0.06 - total_w * 0.0062) * 45) / 375, 1)
                    })

    tidy_df_sample = pd.DataFrame(mock_records)

    # 2. Instantiate your isolated graphics class 
    visualizer = FleetDataVisualizer(output_dir="executive_presentation_charts", palette="Set1")

    # 3. Call the plotting functions directly to save high-resolution .png images to disk
    visualizer.plot_graph_1_fuel_slasher(tidy_df_sample)
    visualizer.plot_graph_2_tradeoff_scatter(tidy_df_sample)
    visualizer.plot_graph_4_braking_safety(tidy_df_sample)
    
    print("\n--- VISUALIZATION MATRIX PIPELINE COMPLETE ---")
    print(f"High-resolution presentation files successfully generated inside local folder: '{visualizer.output_dir}/'")
