import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

class FleetDataVisualizer:
    def __init__(self, output_dir="fleet_reports", palette="Set1"):
        """
        Initializes the visualizer, configures global plotting styles, 
        and ensures a target directory exists to compile file outputs safely.
        """
        self.output_dir = output_dir
        self.palette = palette
        
        # Configure global, clean professional styling defaults
        sns.set_theme(style="whitegrid")
        plt.rcParams.update({
            'font.size': 11,
            'axes.labelsize': 12,
            'axes.titlesize': 14,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'figure.titlesize': 16
        })
        
        # Ensure reporting output path exists natively
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    # =====================================================================
    # INDIVIDUAL GRAPH PLOTTING METHOD BLOCKS
    # =====================================================================

    def plot_graph_1_old_fuel_slasher(self, tidy_df, target_payload=35000):
        """
        Generates the Multi-Speed Fuel Slasher Line Plot (I-95 Flats).
        Isolates a standardized payload to show pure aerodynamic drag velocity decay.
        """
        plt.figure(figsize=(11, 6))
        
        # Filter the long-form dataframe using specific row metrics
        df_flat = tidy_df[
            (tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher') & 
            (tidy_df['Trailer_Payload_lbs'] == target_payload)
        ]
        
        if df_flat.empty:
            print(f"Visualizer Warning: No valid I-95 cruise data found for payload {target_payload} lbs.")
            plt.close()
            return None

        sns.lineplot(
            data=df_flat, x='Speed_MPH', y='Calculated_MPG', 
            hue='Truck_Model', style='Axle_Ratio', 
            markers=True, dashes=True, linewidth=2.5, palette=self.palette
        )

        plt.title(f'Graph 1: Aerodynamic Speed Penalty Matrix\n(Flat Highway Cruise at {target_payload:,} lbs Payload)', fontweight='bold', pad=15)
        plt.xlabel('Vehicle Cruising Speed (MPH)')
        plt.ylabel('Calculated Fuel Efficiency (MPG)')
        
        # Force exact x-axis locks based on known scenario speeds
        unique_speeds = sorted(df_flat['Speed_MPH'].unique())
        plt.xticks(unique_speeds)
        
        plt.legend(title='Configuration Profiles', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_1_fuel_slasher.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_1_fuel_slasher(self, tidy_df, preferred_payload=35000):
        """
        Generates the Multi-Speed Fuel Slasher Line Plot (I-95 Flats).
        Isolates a standardized payload to show pure aerodynamic velocity decay curves.
        """
        # Dynamic Correction: Scan available payload weights in the dataset
        available_payloads = tidy_df['Trailer_Payload_lbs'].unique()
        if len(available_payloads) == 0:
            print("Visualizer Warning: No valid data found for Graph 1.")
            return None
            
        # Fallback logic check
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads[0]

        # Filter the long-form dataframe using specific row metrics
        df_flat = tidy_df[
            (tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher') & 
            (tidy_df['Trailer_Payload_lbs'] == target_payload)
        ]
        
        if df_flat.empty:
            print(f"Visualizer Warning: No valid I-95 cruise rows found for payload {target_payload} lbs.")
            return None

        plt.figure(figsize=(11, 6))
        sns.lineplot(
            data=df_flat, x='Speed_MPH', y='Calculated_MPG', 
            hue='Truck_Model', style='Axle_Ratio', 
            markers=True, dashes=True, linewidth=2.5, palette=self.palette
        )

        # Dynamic Title Labeling
        plt.title(f'Graph 1: Aerodynamic Speed Penalty Corridor Matrix\n(Flat Highway Cruise at {target_payload:,} lbs Payload)', fontweight='bold', pad=15)
        plt.xlabel('Vehicle Cruising Speed (MPH)', labelpad=10)
        plt.ylabel('Calculated Fuel Efficiency (MPG)', labelpad=10)
        
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
        Maps the ultimate physical engineering compromises across all valid rows.
        """
        plt.figure(figsize=(11, 6))
        
        # Filter down to look cleanly at standardized 65MPH cruise baselines
        df_tradeoff = tidy_df[
            (tidy_df['Speed_MPH'] == 65) & 
            (tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher')
        ]

        sns.scatterplot(
            data=df_tradeoff, x='Max_Speed_6pct_Grade_MPH', y='Calculated_MPG',
            hue='Truck_Model', style='Axle_Ratio', size='Trailer_Payload_lbs',
            sizes=(40, 240), palette=self.palette, alpha=0.85
        )

        plt.title('Graph 2: Fleet Performance Trade-Off Mapping Matrix\n(Mountain Climb Velocity vs. Flat Land Fuel Economy)', fontweight='bold', pad=15)
        plt.xlabel('Maximum Attainable Speed Up a 6% Grade (MPH)')
        plt.ylabel('Cruising Fuel Efficiency at 65 MPH (MPG)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_2_performance_tradeoff.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

       # =====================================================================
    # WAVE 1 ADDITIONS: GRAPHS 3, 5, 6, 7, and 8
    # =====================================================================

    def plot_graph_3_kinematics_bars(self, tidy_df):
        """
        Generates the Grouped Kinematics Responsiveness Bar Chart.
        Visually displays 0-50 launch times and 45-65 passing times 
        as a function of shifting trailer weights.
        """
        # Filter down to flat-ground cruising rows to compare pure mechanical acceleration
        df_accel = tidy_df[tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher'].copy()
        if df_accel.empty:
            print("Visualizer Warning: No valid flat-ground data found for Graph 3.")
            return None

        # To plot both metrics side-by-side cleanly, reshape (melt) the timing metrics
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
        axes[0].get_legend().remove()

        # Panel B: 45-65 MPH Passing Responsiveness
        sns.barplot(
            data=df_melted[df_melted['Performance_Metric'] == 'Passing_45_65_s'],
            x='Trailer_Payload_lbs', y='Time_Seconds', hue='Truck_Model',
            palette=self.palette, edgecolor='black', alpha=0.8, ax=axes[1]
        )
        axes[1].set_title('B: 45-65 MPH Highway Passing Sprint')
        axes[1].set_xlabel('Trailer Payload Weight (lbs)')
        axes[1].set_ylabel('') # Y-label is shared
        
        plt.suptitle('Graph 3: Kinematic Performance & Acceleration Timings Scorecard', fontweight='bold', y=0.98)
        plt.legend(title='Vehicle Configuration', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_3_kinematics_bars.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_5_old_route_cost_split(self, tidy_df, diesel_price_per_gal=4.00, def_price_per_gal=5.00):
        """
        Generates the Operating Cost Split Stacked Bar Chart.
        Converts fuel consumption data into fluid expenses per 1,000 miles,
        pre-aggregating category shapes to prevent Seaborn shape mismatches.
        """
        # Filter for a standardized 35,000 lb trailer payload at standard 65 MPH cruise speed
        df_cost = tidy_df[(tidy_df['Speed_MPH'] == 65) & (tidy_df['Trailer_Payload_lbs'] == 35000)].copy()
        if df_cost.empty:
            print("Visualizer Warning: Missing 65 MPH cruising data for Graph 5.")
            return None

        # 1. Operational financial logic calculations
        df_cost['Diesel_Cost_Per_1k_Miles'] = (1000 / df_cost['Calculated_MPG']) * diesel_price_per_gal
        df_cost['DEF_Cost_Per_1k_Miles'] = ((1000 / df_cost['Calculated_MPG']) * 0.04) * def_price_per_gal
        df_cost['Config_Label'] = df_cost['Truck_Model'] + " (" + df_cost['Axle_Ratio'].astype(str) + " Axle)"

        # 2. DYNAMIC CORRECTION: Pre-aggregate data to match Seaborn's structural drawing arrays
        # This collapses your duplicate rows down into exactly 1 unified row per unique config label
        df_agg = df_cost.groupby('Config_Label', as_index=False).mean(numeric_only=True)

        plt.figure(figsize=(12, 6))
        
        # 3. Render stacked bars using the perfectly matched, pre-aggregated DataFrame rows
        # Both bars now natively share a length of exactly 6, preventing Matplotlib shape errors
        sns.barplot(
            data=df_agg, x='Config_Label', y='Diesel_Cost_Per_1k_Miles', 
            color='darkblue', alpha=0.85, label='Diesel Fuel Cost'
        )
        
        sns.barplot(
            data=df_agg, x='Config_Label', y='DEF_Cost_Per_1k_Miles', 
            color='cyan', alpha=0.6, label='DEF Fluid Cost', 
            bottom=df_agg['Diesel_Cost_Per_1k_Miles']  # Perfectly aligned array of length 6!
        )

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

    def plot_graph_5_route_cost_split(self, tidy_df, preferred_payload=35000, diesel_price_per_gal=4.00, def_price_per_gal=5.00):
        """
        Generates the Operating Cost Split Stacked Bar Chart.
        Converts fuel consumption data into fluid expenses per 1,000 miles,
        utilizing a dynamic payload fallback to prevent filtering execution crashes.
        """
        # 1. DYNAMIC CORRECTION: Check available payload weight entries in the dataset
        available_payloads = tidy_df['Trailer_Payload_lbs'].unique()
        
        if len(available_payloads) == 0:
            print("Visualizer Warning: No valid data found for Graph 5 operating costs.")
            return None
            
        # Determine the target payload: use preferred target if present, otherwise grab the first available weight
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads[0]
        
        # Filter for the dynamically determined payload weight at standard 65 MPH cruise speed
        df_cost = tidy_df[(tidy_df['Speed_MPH'] == 65) & (tidy_df['Trailer_Payload_lbs'] == target_payload)].copy()
        
        # If no 65 MPH data exists for that payload, grab the first available speed instead
        if df_cost.empty:
            available_speeds = tidy_df[tidy_df['Trailer_Payload_lbs'] == target_payload]['Speed_MPH'].unique()
            if len(available_speeds) == 0:
                print(f"Visualizer Warning: Missing data rows for payload {target_payload} lbs in Graph 5.")
                return None
            target_speed = available_speeds[0]
            df_cost = tidy_df[(tidy_df['Speed_MPH'] == target_speed) & (tidy_df['Trailer_Payload_lbs'] == target_payload)].copy()
            print(f"[Visualizer Notification]: Graph 5 falling back to speed {target_speed} MPH for payload {target_payload} lbs.")
        else:
            print(f"[Visualizer Notification]: Graph 5 processing operating costs at standard 65 MPH / {target_payload:,} lbs payload.")

        # 2. Operational financial logic calculations
        df_cost['Diesel_Cost_Per_1k_Miles'] = (1000 / df_cost['Calculated_MPG']) * diesel_price_per_gal
        df_cost['DEF_Cost_Per_1k_Miles'] = ((1000 / df_cost['Calculated_MPG']) * 0.04) * def_price_per_gal
        df_cost['Config_Label'] = df_cost['Truck_Model'] + " (" + df_cost['Axle_Ratio'].astype(str) + " Axle)"

        # 3. Pre-aggregate data to handle duplicate configuration entries cleanly
        df_agg = df_cost.groupby('Config_Label', as_index=False).mean(numeric_only=True)

        plt.figure(figsize=(12, 6))
        
        # 4. Render stacked bars using the shape-validated DataFrame
        sns.barplot(
            data=df_agg, x='Config_Label', y='Diesel_Cost_Per_1k_Miles', 
            color='darkblue', alpha=0.85, label='Diesel Fuel Cost'
        )
        
        sns.barplot(
            data=df_agg, x='Config_Label', y='DEF_Cost_Per_1k_Miles', 
            color='cyan', alpha=0.6, label='DEF Fluid Cost', 
            bottom=df_agg['Diesel_Cost_Per_1k_Miles']
        )

        plt.title(f'Graph 5: Route Operating Fluid Cost Comparison\n(Projected Expenses Per 1,000 Miles at {df_cost["Speed_MPH"].iloc[0]} MPH / {target_payload:,} lbs Payload)', fontweight='bold', pad=15)
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
            print("Visualizer Warning: Missing rolling terrain ('I40_Midwest_Rhythm') entries for Graph 6.")
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
        sns.heatmap(
            heatmap_data, annot=True, fmt=".1f", cmap="RdYlGn_r", 
            cbar_kws={'label': 'Gear Hunting Risk Rating (1=Stable, 10=Severe)'}, 
            linewidths=0.5
        )

        plt.title('Graph 6: Transmission Stability & Gear Hunting Risk Matrix\n(Continuous Hill Cruising Over Shifting Trailer Payloads)', fontweight='bold', pad=15)
        plt.xlabel('Trailer Payload Weight (lbs)')
        plt.ylabel('Drivetrain Rear End Axle Ratio')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_6_gear_hunting_heatmap.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path
    def plot_graph_6_gear_flexibility_hardcoded(self, tidy_df):
        """
        REWRITE SUITE: Generates the Gear Flexibility and Headroom Cushion Chart.
        Plots the exact speed drop (MPH) or grade increase (% Incline) required 
        to force a transmission gear change.
        """
        # Filter for a standard loaded trailer configuration on rolling terrain
        df_hills = tidy_df[tidy_df['Route_Scenario'] == 'I40_Midwest_Rhythm'].copy()
        if df_hills.empty:
            print("Visualizer Warning: Missing rolling terrain entries for Graph 6.")
            return None

        # --- DYNAMIC PHYSICS HEADROOM CALCULATIONS ---
        # Metric 1 proxy: Speed drop allowed before falling out of the engine's torque plateau
        # Metric 2 proxy: Grade percentage increase allowed before overwhelming peak engine torque
        df_hills['Speed_Cushion_MPH'] = (df_hills['Engine_Cruise_RPM'] - 1000) * 60.0 / (529 * df_hills['Axle_Ratio'].astype(float))
        df_hills['Speed_Cushion_MPH'] = df_hills['Speed_Cushion_MPH'].clip(lower=1.0, upper=20.0)
        
        df_hills['Grade_Cushion_Pct'] = (100.0 - df_hills['Engine_Load_Pct']) * 0.05
        df_hills['Grade_Cushion_Pct'] = df_hills['Grade_Cushion_Pct'].clip(lower=0.2, upper=4.0)

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Panel A: Speed Cushion Matrix (Passing Flexibility)
        sns.barplot(
            data=df_hills, x='Axle_Ratio', y='Speed_Cushion_MPH', hue='Truck_Model',
            palette=self.palette, edgecolor='black', alpha=0.8, ax=axes[0]
        )
        axes[0].set_title('A: Speed Change Buffer Before Shift\n(Maximum Speed Drop Allowed in Top Gear)')
        axes[0].set_xlabel('Drivetrain Rear End Axle Ratio')
        axes[0].set_ylabel('Speed Delta Cushion (MPH - Higher is More Stable)')

        # Panel B: Grade Cushion Matrix (Terrain Forgiveness)
        sns.barplot(
            data=df_hills, x='Axle_Ratio', y='Grade_Cushion_Pct', hue='Truck_Model',
            palette=self.palette, edgecolor='black', alpha=0.8, ax=axes[1]
        )
        axes[1].set_title('B: Terrain Grade Buffer Before Shift\n(Maximum Grade Increase Allowed in Top Gear)')
        axes[1].set_xlabel('Drivetrain Rear End Axle Ratio')
        axes[1].set_ylabel('Incline Delta Cushion (% Grade Incline - Higher is More Stable)')

        plt.suptitle('Graph 6: Transmission Stability & Gear Headroom Metrics', fontweight='bold', y=0.98)
        plt.legend(title='Vehicle Profile', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_6_gear_flexibility.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path
    def plot_graph_6_gear_flexibility(self, tidy_df):
        """
        Generates the Gear Flexibility and Headroom Cushion Chart.
        Plots the exact speed drop (MPH) or grade increase (% Incline) 
        required to force a transmission gear change by reading pre-calculated
        physics columns directly from the long-form DataFrame.
        """
        # Isolate the rolling hills route profile where gear hunting actively manifests
        df_hills = tidy_df[tidy_df['Route_Scenario'] == 'I40_Midwest_Rhythm'].copy()
        
        if df_hills.empty:
            print("Visualizer Warning: Missing rolling terrain entries ('I40_Midwest_Rhythm') for Graph 6.")
            return None

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Panel A: Speed Cushion Matrix (Passing Flexibility)
        # Natively reads 'Speed_Cushion_MPH' calculated by Module 2 using truck-specific tire revs and RPM bounds
        sns.barplot(
            data=df_hills, x='Axle_Ratio', y='Speed_Cushion_MPH', hue='Truck_Model',
            palette=self.palette, edgecolor='black', alpha=0.8, ax=axes[0], errorbar=None
        )
        axes[0].set_title('A: Speed Change Buffer Before Shift\n(Maximum Speed Drop Allowed in Top Gear)')
        axes[0].set_xlabel('Drivetrain Rear End Axle Ratio')
        axes[0].set_ylabel('Speed Delta Cushion (MPH - Higher is More Stable)')

        # Panel B: Grade Cushion Matrix (Terrain Forgiveness)
        # Natively reads 'Grade_Cushion_Pct' calculated dynamically by Module 2's force-balance engine
        sns.barplot(
            data=df_hills, x='Axle_Ratio', y='Grade_Cushion_Pct', hue='Truck_Model',
            palette=self.palette, edgecolor='black', alpha=0.8, ax=axes[1],errorbar=None
        )
        axes[1].set_title('B: Terrain Grade Buffer Before Shift\n(Maximum Grade Increase Allowed in Top Gear)')
        axes[1].set_xlabel('Drivetrain Rear End Axle Ratio')
        axes[1].set_ylabel('Incline Delta Cushion (% Grade Incline - Higher is More Stable)')

        plt.suptitle('Graph 6: Transmission Stability & Gear Headroom Metrics', fontweight='bold', y=0.98)
        
        # Ensure only the rightmost panel holds a clean single legend block to avoid dual clutter
        if axes[0].get_legend(): axes[0].get_legend().remove()
        axes[1].legend(title='Vehicle Profile', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_6_gear_flexibility.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path



    def plot_graph_7_lugging_risk_RPM_old(self, tidy_df):
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

        # Draw a horizontal warning indicator mapping standard Class 8 torque plateau drops
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


    def plot_graph_7_lugging_risk_RPM_v2(self, tidy_df):
        """
        REWRITE SUITE: Generates the Real Mountain Shifting Sawtooth Curve.
        Plots true engine RPM and active gear steps across forced climbing speeds.
        """
        df_mountain = tidy_df[tidy_df['Route_Scenario'] == 'I70_Mountain_Conqueror'].copy()
        if df_mountain.empty:
            print("Visualizer Warning: No real mountain data found for Graph 7.")
            return None

        plt.figure(figsize=(11, 6))
        
        # Plot true gear-swept mountain RPM lines
        sns.lineplot(
            data=df_mountain, x='Speed_MPH', y='Engine_Cruise_RPM', 
            hue='Truck_Model', style='Axle_Ratio', markers=True, linewidth=2.5, palette=self.palette
        )

        # Draw structural safety limits
        plt.axhline(y=1000, color='red', linestyle='--', linewidth=2, label='Class 8 Torque Drop Threshold (1,000 RPM)')
        plt.axhline(y=1600, color='darkgreen', linestyle=':', linewidth=1.5, label='Ford 6.7L HO Torque Start (1,600 RPM)')
        plt.axhspan(600, 1000, color='red', alpha=0.05, label='Severe Low-End Lugging Zone')

        plt.title('Graph 7: Real Mountain Climb Shifting & Engine RPM Map\n(True Transmission Downshift Pacing Across Forced climbing Speeds on a 6% Grade)', fontweight='bold', pad=15)
        plt.xlabel('Forced Climb Vehicle Speed (MPH)', labelpad=10)
        plt.ylabel('Engine Operational Speed (RPM)', labelpad=10)
        plt.ylim(500, 2800)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_7_lugging_risk_boundaries.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path
    def plot_graph_7_lugging_risk_RPM(self, tidy_df):
        """
        Generates the Real Mountain Shifting Sawtooth Curve.
        Plots true engine RPM across a continuous array of possible climbing speeds.
        """
        df_mountain = tidy_df[tidy_df['Route_Scenario'] == 'I70_Mountain_Conqueror'].copy()
        if df_mountain.empty:
            print("Visualizer Warning: No real mountain data found for Graph 7.")
            return None

        plt.figure(figsize=(11, 6))
        
        # Draw clean lines mapping engine rotation speed. 
        # The line will naturally track the transmission's downshifts.
        sns.lineplot(
            data=df_mountain, x='Speed_MPH', y='Engine_Cruise_RPM', 
            hue='Truck_Model', style='Axle_Ratio', markers=True, linewidth=2.5, palette=self.palette
        )

        # Clear, actionable horizontal safety lines
        plt.axhline(y=1000, color='red', linestyle='--', linewidth=2, label='Class 8 Torque Drop Threshold (1,000 RPM)')
        plt.axhline(y=1600, color='darkgreen', linestyle=':', linewidth=1.5, label='Ford 6.7L HO Torque Start (1,600 RPM)')
        plt.axhspan(600, 1000, color='red', alpha=0.05, label='Severe Low-End Lugging Zone')

        plt.title('Graph 7: Real Mountain Climb Shifting & Engine RPM Map\n(True Transmission Downshift Pacing Across a Continuous Array of climbing Speeds)', fontweight='bold', pad=15)
        plt.xlabel('Climbing Road Speed (MPH)', labelpad=10)
        plt.ylabel('Engine Operational Speed (RPM)', labelpad=10)
        
        # Dynamically set the x-limits to match whatever the fastest truck in the fleet can do up the hill
        max_x = min(75.0, df_mountain['Speed_MPH'].max() + 5)
        plt.xlim(10, max_x)
        plt.ylim(500, 2800)
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_7_lugging_risk_boundaries.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path



    def plot_graph_8_old_speed_penalty_ROI(self, tidy_df):
        """
        Generates the Time Saved vs. Fuel Lost ROI Cross Plot.
        Visualizes the economic point of diminishing financial returns.
        """
        # Filter for standard flat long-haul configurations
        df_roi = tidy_df[
            (tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher') & 
            (tidy_df['Trailer_Payload_lbs'] == 35000)
        ].copy()
        
        if df_roi.empty:
            print("Visualizer Warning: Missing long-haul data rows for Graph 8.")
            return None

        # Build baseline kinematics variables over a 100,000 mile lifecycle
        df_roi['Annual_Windshield_Hours'] = 100000 / df_roi['Speed_MPH']
        df_roi['Annual_Fuel_Bill_Dollars'] = (100000 / df_roi['Calculated_MPG']) * 4.00

        # Group data by tested speed to isolate global averages
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

        # Y-Axis 2: Instantiate a twin coordinate layer sharing the same X-axis
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

    def plot_graph_8_speed_penalty_ROI_wrong(self, tidy_df, preferred_payload=35000):
        """
        Generates the Time Saved vs. Fuel Lost ROI Cross Plot.
        Visualizes the economic point of diminishing financial returns.
        """
        # Dynamic Correction: Scan available long-haul payload entries
        df_flat = tidy_df[tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher']
        available_payloads = df_flat['Trailer_Payload_lbs'].unique()
        
        if len(available_payloads) == 0:
            print("Visualizer Warning: No valid data found for Graph 8.")
            return None
            
        # Fallback logic check
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads[0]

        df_roi = df_flat[df_flat['Trailer_Payload_lbs'] == target_payload].copy()
        if df_roi.empty:
            print("Visualizer Warning: Missing long-haul rows for Graph 8.")
            return None

        df_roi['Annual_Windshield_Hours'] = 100000 / df_roi['Speed_MPH']
        df_roi['Annual_Fuel_Bill_Dollars'] = (100000 / df_roi['Calculated_MPG']) * 4.00

        df_grouped = df_roi.groupby('Speed_MPH', as_index=False).mean(numeric_only=True)

        fig, ax1 = plt.subplots(figsize=(10, 6))

        color = 'tab:red'
        ax1.set_xlabel('Target Cruising Speed (MPH)', fontsize=12)
        ax1.set_ylabel('Average Annual Fuel Expense ($)', color=color, fontsize=12)
        line1 = ax1.plot(df_grouped['Speed_MPH'], df_grouped['Annual_Fuel_Bill_Dollars'], color=color, marker='o', linewidth=3, label='Annual Fuel Bill ($)')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, linestyle=':', alpha=0.6)

        ax2 = ax1.twinx()  
        color = 'tab:blue'
        ax2.set_ylabel('Annual Driver Windshield Hours (Hrs)', color=color, fontsize=12)
        line2 = ax2.plot(df_grouped['Speed_MPH'], df_grouped['Annual_Windshield_Hours'], color=color, marker='s', linewidth=3, linestyle='--', label='Windshield Time (Hours)')
        ax2.tick_params(axis='y', labelcolor=color)

        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper center')

        # Dynamic Title Labeling
        plt.title(f'Graph 8: Fleet Velocity ROI Return Matrix\n(Annual Fuel Dollars Spent vs. Windshield Hours Saved Over 100,000 Miles at {target_payload:,} lbs Payload)', fontweight='bold', pad=15)
        fig.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_8_speed_penalty_roi.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path
    def plot_graph_8_speed_penalty_ROI_singlegraph(self, tidy_df, preferred_model=None, preferred_axle=None, preferred_payload=35000):
        """
        Generates the Time Saved vs. Fuel Lost ROI Cross Plot.
        Isolates a single, specific truck and axle profile to prevent 
        invalid aggregation corruption across different fleet vehicle classes.
        """
        # 1. DYNAMIC CORRECTION: Isolate flat long-haul scenarios
        df_flat = tidy_df[tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher'].copy()
        if df_flat.empty:
            print("Visualizer Warning: Missing long-haul data rows for Graph 8.")
            return None

        # Resolve payload fallback dynamically
        available_payloads = df_flat['Trailer_Payload_lbs'].unique()
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads
        df_flat = df_flat[df_flat['Trailer_Payload_lbs'] == target_payload]

        # 2. VEHICLE PROFILE SELECTION GATEKEEPER
        # If no explicit truck is requested, automatically grab the first available model/axle combination
        available_models = df_flat['Truck_Model'].unique()
        if len(available_models) == 0:
            print("Visualizer Warning: No valid truck models found for Graph 8.")
            return None
            
        target_model = preferred_model if preferred_model in available_models else available_models[0]
        df_model = df_flat[df_flat['Truck_Model'] == target_model]
        
        available_axles = df_model['Axle_Ratio'].unique()
        target_axle = preferred_axle if preferred_axle in available_axles else available_axles[0]
        
        # Isolate down to a single, mathematically pure configuration vector row set!
        df_roi = df_model[df_model['Axle_Ratio'] == target_axle].copy()
        
        if df_roi.empty:
            print(f"Visualizer Warning: No rows matching {target_model} with {target_axle} axle for Graph 8.")
            return None

        # 3. Build baseline variables over a 100,000 mile lifecycle for THIS specific truck
        df_roi['Annual_Windshield_Hours'] = 100000 / df_roi['Speed_MPH']
        df_roi['Annual_Fuel_Bill_Dollars'] = (100000 / df_roi['Calculated_MPG']) * 4.00

        # Sort cleanly by speed to ensure smooth dual-axis plotting
        df_grouped = df_roi.sort_values('Speed_MPH')

        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Y-Axis 1: Plot the Annual Fuel Bill curve in bold red
        color = 'tab:red'
        ax1.set_xlabel('Target Cruising Speed (MPH)', fontsize=12, labelpad=10)
        ax1.set_ylabel('Average Annual Fuel Expense ($)', color=color, fontsize=12, labelpad=10)
        line1 = ax1.plot(
            df_grouped['Speed_MPH'], df_grouped['Annual_Fuel_Bill_Dollars'], 
            color=color, marker='o', linewidth=3, label='Annual Fuel Bill ($)'
        )
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
        ax1.grid(True, linestyle=':', alpha=0.6)

        # Y-Axis 2: Instantly instantiate a twin coordinate layer sharing the same X-axis
        ax2 = ax1.twinx()  
        color = 'tab:blue'
        ax2.set_ylabel('Annual Driver Windshield Hours (Hrs)', color=color, fontsize=12, labelpad=10)
        line2 = ax2.plot(
            df_grouped['Speed_MPH'], df_grouped['Annual_Windshield_Hours'], 
            color=color, marker='s', linewidth=3, linestyle='--', label='Windshield Time (Hours)'
        )
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} hrs".format(int(x))))

        # Merge the distinct dual axes labels into a single integrated visual box legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper center')

        # Dynamic Title explicitly stating the isolated profile parameters
        plt.title(f'Graph 8: Fleet Velocity ROI Return Matrix\nIsolates: {target_model} ({target_axle} Axle) at {target_payload:,} lbs Payload', fontweight='bold', pad=15)
        fig.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_8_speed_penalty_roi.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        
        print(f"[Visualizer Notification]: Graph 8 successfully isolated and plotted '{target_model} ({target_axle} Axle)' data profile.")
        return save_path

    def plot_graph_8_speed_penalty_ROI_logicerr0r(self, tidy_df, preferred_payload=35000, generate_individual_profiles=False):
        """
        Generates the Fleet Velocity ROI Return Matrix (Graph 8).
        Default behavior: Compiles a clean, multi-line comparison dashboard separating 
        unique truck profiles to allow direct economic side-by-side selection.
        If generate_individual_profiles=True, it additionally exports independent, 
        parameterized standalone cross-plots for every truck/axle combination.
        """
        # 1. Filter long-haul scenarios and isolate target payload fallback
        df_flat = tidy_df[tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher'].copy()
        if df_flat.empty:
            print("Visualizer Warning: Missing long-haul data rows for Graph 8.")
            return None

        available_payloads = df_flat['Trailer_Payload_lbs'].unique()
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads
        df_flat = df_flat[df_flat['Trailer_Payload_lbs'] == target_payload].copy()

        # Build clean unique configuration strings for line legends (prevents cross-truck aggregation bugs)
        df_flat['Config_Profile'] = df_flat['Truck_Model'] + " (" + df_flat['Axle_Ratio'].astype(str) + " Axle)"
        
        # Calculate 100,000-mile operational lifecycle line items
        df_flat['Annual_Fuel_Bill_Dollars'] = (100000 / df_flat['Calculated_MPG']) * 4.00
        df_flat['Annual_Windshield_Hours'] = 100000 / df_flat['Speed_MPH']
        
        df_flat = df_flat.sort_values('Speed_MPH')

        # =====================================================================
        # DEFAULT MODE: MULTI-LINE COMPARISON DASHBOARD PANEL
        # =====================================================================
        fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
        
        # Panel A: Multi-Line Fleet Fuel Cost Expenditure Curves
        sns.lineplot(
            data=df_flat, x='Speed_MPH', y='Annual_Fuel_Bill_Dollars', 
            hue='Config_Profile', marker='o', linewidth=2.5, palette=self.palette, ax=axes[0]
        )
        axes[0].set_title('A: Annual Fuel Expenditure Lifecycle\n(Based on 100,000 Annual Miles at $4.00/gal)', fontsize=11, fontweight='semibold')
        axes[0].set_xlabel('Target Cruising Speed (MPH)', labelpad=10)
        axes[0].set_ylabel('Annual Fuel Expense ($)', labelpad=10)
        axes[0].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
        axes[0].set_xticks(sorted(df_flat['Speed_MPH'].unique()))
        axes[0].legend().remove() # Unified legend placed on the right block

        # Panel B: Multi-Line Windshield Hours Saved Matrix
        # Note: Windshield hours are a pure function of speed, but line split preserves legend alignment
        sns.lineplot(
            data=df_flat, x='Speed_MPH', y='Annual_Windshield_Hours', 
            hue='Config_Profile', marker='s', linewidth=2.5, linestyle='--', palette=self.palette, ax=axes[1]
        )
        axes[1].set_title('B: Annual Driver Windshield Time\n(Total Clock Hours Required to Complete 100,000 Miles)', fontsize=11, fontweight='semibold')
        axes[1].set_xlabel('Target Cruising Speed (MPH)', labelpad=10)
        axes[1].set_ylabel('Driver Windshield Time (Hours)', labelpad=10)
        axes[1].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} hrs".format(int(x))))
        axes[1].set_xticks(sorted(df_flat['Speed_MPH'].unique()))
        
        plt.suptitle(f'Graph 8: Fleet Velocity ROI Return Matrix\n(Comparative Multi-Line Sweep at {target_payload:,} lbs Trailer Payload)', fontweight='bold', y=0.98)
        axes[1].legend(title='Vehicle Config Profile', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        master_save_path = os.path.join(self.output_dir, "graph_8_fleet_roi_comparison.png")
        plt.savefig(master_save_path, dpi=300)
        plt.close()
        print(f"[Visualizer Master Log]: Compiled multi-line comparison sheet -> '{master_save_path}'")

        # =====================================================================
        # OPTIONAL SWITCH MODE: INDEPENDENT GENERATION PER PERMUTATION
        # =====================================================================
        if generate_individual_profiles:
            unique_configs = df_flat['Config_Profile'].unique()
            print(f"[Supervisor Info]: Processing switch loop... Exporting {len(unique_configs)} isolated cross-plots.")
            
            for config in unique_configs:
                df_sub = df_flat[df_flat['Config_Profile'] == config]
                
                fig, ax1 = plt.subplots(figsize=(10, 6))
                
                # Draw single asset fuel line
                color = 'tab:red'
                ax1.set_xlabel('Target Cruising Speed (MPH)', fontsize=11, labelpad=10)
                ax1.set_ylabel('Annual Fuel Expense ($)', color=color, fontsize=11, labelpad=10)
                line1 = ax1.plot(df_sub['Speed_MPH'], df_sub['Annual_Fuel_Bill_Dollars'], color=color, marker='o', linewidth=3, label='Annual Fuel Bill ($)')
                ax1.tick_params(axis='y', labelcolor=color)
                ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
                ax1.grid(True, linestyle=':', alpha=0.6)

                # Draw twin axis time line
                ax2 = ax1.twinx()  
                color = 'tab:blue'
                ax2.set_ylabel('Annual Driver Windshield Hours (Hrs)', color=color, fontsize=11, labelpad=10)
                line2 = ax2.plot(df_sub['Speed_MPH'], df_sub['Annual_Windshield_Hours'], color=color, marker='s', linewidth=3, linestyle='--', label='Windshield Time (Hours)')
                ax2.tick_params(axis='y', labelcolor=color)
                ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} hrs".format(int(x))))

                lines = line1 + line2
                labels = [l.get_label() for l in lines]
                ax1.legend(lines, labels, loc='upper center')

                plt.title(f'Isolated Velocity ROI Cross-Plot\nVehicle Target: {config}', fontweight='bold', pad=15)
                fig.tight_layout()
                
                # Sanitize text elements to construct file names
                file_slug = config.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
                sub_save_name = f"graph_8_roi_{file_slug}.png"
                sub_save_path = os.path.join(self.output_dir, sub_save_name)
                
                plt.savefig(sub_save_path, dpi=300)
                plt.close()
                
        return master_save_path
    def plot_graph_8_speed_penalty_ROI(self, tidy_df, preferred_payload=35000, generate_individual_profiles=False):
        """
        Generates the Fleet Velocity ROI Return Matrix (Graph 8).
        """
        df_flat = tidy_df[tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher'].copy()
        if df_flat.empty:
            print("Visualizer Warning: Missing long-haul data rows for Graph 8.")
            return None

        available_payloads = df_flat['Trailer_Payload_lbs'].unique()
        
        # DYNAMIC SCALAR FIX: Slice index [0] to extract a pure scalar integer if fallback triggers
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads[0]
        df_flat = df_flat[df_flat['Trailer_Payload_lbs'] == target_payload].copy()

        df_flat['Config_Profile'] = df_flat['Truck_Model'] + " (" + df_flat['Axle_Ratio'].astype(str) + " Axle)"
        df_flat['Annual_Fuel_Bill_Dollars'] = (100000 / df_flat['Calculated_MPG']) * 4.00
        df_flat['Annual_Windshield_Hours'] = 100000 / df_flat['Speed_MPH']
        df_flat = df_flat.sort_values('Speed_MPH')

        fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
        
        sns.lineplot(data=df_flat, x='Speed_MPH', y='Annual_Fuel_Bill_Dollars', hue='Config_Profile', marker='o', linewidth=2.5, palette=self.palette, ax=axes[0])
        axes[0].set_title('A: Annual Fuel Expenditure Lifecycle\n(Based on 100,000 Annual Miles at $4.00/gal)', fontsize=11, fontweight='semibold')
        axes[0].set_xlabel('Target Cruising Speed (MPH)', labelpad=10)
        axes[0].set_ylabel('Annual Fuel Expense ($)', labelpad=10)
        axes[0].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
        axes[0].set_xticks(sorted(df_flat['Speed_MPH'].unique()))
        if axes[0].get_legend(): axes[0].get_legend().remove()

        sns.lineplot(data=df_flat, x='Speed_MPH', y='Annual_Windshield_Hours', hue='Config_Profile', marker='s', linewidth=2.5, linestyle='--', palette=self.palette, ax=axes[1])
        axes[1].set_title('B: Annual Driver Windshield Time\n(Total Clock Hours Required to Complete 100,000 Miles)', fontsize=11, fontweight='semibold')
        axes[1].set_xlabel('Target Cruising Speed (MPH)', labelpad=10)
        axes[1].set_ylabel('Driver Windshield Time (Hours)', labelpad=10)
        axes[1].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} hrs".format(int(x))))
        axes[1].set_xticks(sorted(df_flat['Speed_MPH'].unique()))
        
        plt.suptitle(f'Graph 8: Fleet Velocity ROI Return Matrix\n(Comparative Multi-Line Sweep at {target_payload:,} lbs Trailer Payload)', fontweight='bold', y=0.98)
        
        if axes[1].get_legend(): axes[1].get_legend().remove()
        axes[1].legend(title='Vehicle Config Profile', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        master_save_path = os.path.join(self.output_dir, "graph_8_fleet_roi_comparison.png")
        plt.savefig(master_save_path, dpi=300)
        plt.close()
        print(f"[Visualizer Master Log]: Compiled multi-line comparison sheet -> '{master_save_path}'")

        if generate_individual_profiles:
            unique_configs = df_flat['Config_Profile'].unique()
            for config in unique_configs:
                df_sub = df_flat[df_flat['Config_Profile'] == config]
                fig, ax1 = plt.subplots(figsize=(10, 6))
                
                color = 'tab:red'
                ax1.set_xlabel('Target Cruising Speed (MPH)', fontsize=11, labelpad=10)
                ax1.set_ylabel('Annual Fuel Expense ($)', color=color, fontsize=11, labelpad=10)
                line1 = ax1.plot(df_sub['Speed_MPH'], df_sub['Annual_Fuel_Bill_Dollars'], color=color, marker='o', linewidth=3, label='Annual Fuel Bill ($)')
                ax1.tick_params(axis='y', labelcolor=color)
                ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
                ax1.grid(True, linestyle=':', alpha=0.6)

                ax2 = ax1.twinx()  
                color = 'tab:blue'
                ax2.set_ylabel('Annual Driver Windshield Hours (Hrs)', color=color, fontsize=11, labelpad=10)
                line2 = ax2.plot(df_sub['Speed_MPH'], df_sub['Annual_Windshield_Hours'], color=color, marker='s', linewidth=3, linestyle='--', label='Windshield Time (Hours)')
                ax2.tick_params(axis='y', labelcolor=color)
                ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} hrs".format(int(x))))

                lines = line1 + line2
                labels = [l.get_label() for l in lines]
                ax1.legend(lines, labels, loc='upper center')

                plt.title(f'Isolated Velocity ROI Cross-Plot\nVehicle Target: {config}', fontweight='bold', pad=15)
                fig.tight_layout()
                
                file_slug = config.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
                sub_save_path = os.path.join(self.output_dir, f"graph_8_roi_{file_slug}.png")
                plt.savefig(sub_save_path, dpi=300)
                plt.close()
                
        return master_save_path

    
    def plot_graph_4_old_2_braking_safety(self, tidy_df, descent_speed=45):
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
            print(f"Visualizer Warning: No valid I-70 mountain data found for speed {descent_speed} MPH.")
            plt.close()
            return None

        sns.barplot(
            data=df_braking, x='Trailer_Payload_lbs', y='Downhill_Req_Braking_HP',
            hue='Truck_Model', palette=self.palette, ax=ax, edgecolor='black', alpha=0.8
        )

        # Apply structural safety capacity thresholds (hard constraints)
        ax.axhline(y=250, color='red', linestyle='--', linewidth=2, label='Ford 6.7L HO Exhaust Brake Max (250 HP)')
        ax.axhline(y=450, color='orange', linestyle='-.', linewidth=2, label='Cummins X15 Efficiency Jake Max (450 HP)')
        ax.axhline(y=530, color='darkgreen', linestyle=':', linewidth=2, label='Volvo D13TC Engine Brake Max (530 HP)')

        ax.set_title(f'Graph 4: Downhill Compression Brake Safety Limits\n(Continuous Horsepower Demanded to Hold {descent_speed} MPH Down a 6% Grade)', fontweight='bold', pad=15)
        ax.set_xlabel('Trailer Payload Weight (lbs)')
        ax.set_ylabel('Required Continuous Retarding Power (HP)')
        ax.set_ylim(0, 600)

        # Highlight the high risk service brake fade zone above Ford capacity
        ax.axhspan(250, 600, color='red', alpha=0.04)

        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_4_braking_safety.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path


    def plot_graph_4_old_braking_safety(self, tidy_df, preferred_descent_speed=45):
        """
        Generates the Downhill Descent Control Threshold Bar Plot.
        Maps dynamic brake wear zones as a function of changing trailer loads.
        """
        # Dynamic Correction: Scan available mountain descent speeds in the dataset
        df_mth = tidy_df[tidy_df['Route_Scenario'] == 'I70_Mountain_Conqueror']
        available_speeds = df_mth['Speed_MPH'].unique()
        
        if len(available_speeds) == 0:
            print("Visualizer Warning: No valid mountain data found for Graph 4.")
            return None
            
        # Fallback logic check
        descent_speed = preferred_descent_speed if preferred_descent_speed in available_speeds else available_speeds[0]

        fig, ax = plt.subplots(figsize=(11, 6))
        df_braking = df_mth[df_mth['Speed_MPH'] == descent_speed].copy()
        df_braking = df_braking.drop_duplicates(subset=['Truck_Model', 'Trailer_Payload_lbs'])

        sns.barplot(
            data=df_braking, x='Trailer_Payload_lbs', y='Downhill_Req_Braking_HP',
            hue='Truck_Model', palette=self.palette, ax=ax, edgecolor='black', alpha=0.8
        )

        ax.axhline(y=250, color='red', linestyle='--', linewidth=2, label='Ford 6.7L HO Exhaust Brake Max (250 HP)')
        ax.axhline(y=450, color='orange', linestyle='-.', linewidth=2, label='Cummins X15 Efficiency Jake Max (450 HP)')
        ax.axhline(y=530, color='darkgreen', linestyle=':', linewidth=2, label='Volvo D13TC Engine Brake Max (530 HP)')
        ax.axhspan(250, 600, color='red', alpha=0.03, label='Critical Brake Fade Zone (Foot Assist Required)')

        # Dynamic Title Labeling
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

    def plot_graph_4_braking_safety(self, tidy_df, preferred_descent_speed=45):
        """
        Generates the Downhill Descent Control Threshold Bar Plot.
        Maps dynamic brake wear zones as a function of changing trailer loads.
        """
        # Dynamic Correction: Scan available mountain descent speeds in the dataset
        df_mth = tidy_df[tidy_df['Route_Scenario'] == 'I70_Mountain_Conqueror']
        available_speeds = df_mth['Speed_MPH'].unique()
        
        if len(available_speeds) == 0:
            print("Visualizer Warning: No valid mountain data found for Graph 4.")
            return None
            
        # Fallback logic check
        descent_speed = preferred_descent_speed if preferred_descent_speed in available_speeds else available_speeds[0]

        fig, ax = plt.subplots(figsize=(11, 6))
        df_braking = df_mth[df_mth['Speed_MPH'] == descent_speed].copy()
        df_braking = df_braking.drop_duplicates(subset=['Truck_Model', 'Trailer_Payload_lbs'])

        sns.barplot(
            data=df_braking, x='Trailer_Payload_lbs', y='Downhill_Req_Braking_HP',
            hue='Truck_Model', palette=self.palette, ax=ax, edgecolor='black', alpha=0.8
        )

        ax.axhline(y=250, color='red', linestyle='--', linewidth=2, label='Ford 6.7L HO Exhaust Brake Max (250 HP)')
        ax.axhline(y=450, color='orange', linestyle='-.', linewidth=2, label='Cummins X15 Efficiency Jake Max (450 HP)')
        ax.axhline(y=530, color='darkgreen', linestyle=':', linewidth=2, label='Volvo D13TC Engine Brake Max (530 HP)')
        ax.axhspan(250, 600, color='red', alpha=0.03, label='Critical Brake Fade Zone (Foot Assist Required)')

        # Dynamic Title Labeling
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
    # THE SUPERVISOR / WRAPPER REPORTING LAYER
    # =====================================================================

    def generate_executive_visual_report(self, tidy_df, active_graph_ids=[1, 2, 3, 4, 5, 6, 7, 8]):
        """
        The supervisor coordinator. Processes a selected list of graph targets,
        coordinates individual data extraction loops, and prints execution summary logs.
        
        Parameters:
        - tidy_df: The master long-format Pandas DataFrame generated by your simulation.
        - active_graph_ids: A list of integers matching the Graph IDs you wish to render.
        """
        print(f"\n--- VISUAL REPORT SUPERVISOR STARTING: compiling outputs to '{self.output_dir}/' ---")
        generated_files = {}

        # -----------------------------------------------------------------
        # WAVE 1 BASELINE PLOTS (1, 2, and 4)
        # -----------------------------------------------------------------
        if 1 in active_graph_ids:
            path = self.plot_graph_1_fuel_slasher(tidy_df)
            if path: 
                generated_files['Graph 1'] = path
            print("[Supervisor Log]: Compiled Graph 1 (Fuel Line Plot)")

        if 2 in active_graph_ids:
            path = self.plot_graph_2_tradeoff_scatter(tidy_df)
            if path: 
                generated_files['Graph 2'] = path
            print("[Supervisor Log]: Compiled Graph 2 (Drivetrain Tradeoff Scatter)")

        if 4 in active_graph_ids:
            path = self.plot_graph_4_braking_safety(tidy_df)
            if path: 
                generated_files['Graph 4'] = path
            print("[Supervisor Log]: Compiled Graph 4 (Braking Threshold Bars)")

        # -----------------------------------------------------------------
        # NEW WAVE 1 ADDITIONS (3, 5, 6, 7, and 8)
        # -----------------------------------------------------------------
        if 3 in active_graph_ids:
            path = self.plot_graph_3_kinematics_bars(tidy_df)
            if path: 
                generated_files['Graph 3'] = path
            print("[Supervisor Log]: Compiled Graph 3 (Kinematics Timing Bars)")

        if 5 in active_graph_ids:
            path = self.plot_graph_5_route_cost_split(tidy_df)
            if path: 
                generated_files['Graph 5'] = path
            print("[Supervisor Log]: Compiled Graph 5 (Diesel vs DEF Cost Splits)")

        if 6 in active_graph_ids:
            path = self.plot_graph_6_gear_hunting_heatmap(tidy_df)
            if path: 
                generated_files['Graph 6'] = path
            print("[Supervisor Log]: Compiled Graph 6 (Gear Hunting Stability Heatmap)")

        if 6 in active_graph_ids:
            path = self.plot_graph_6_gear_flexibility(tidy_df)
            if path: 
                generated_files['Graph 6a'] = path
            print("[Supervisor Log]: Compiled Graph 6a (Gear Flexibility)")

        if 7 in active_graph_ids:
            path = self.plot_graph_7_lugging_risk_RPM(tidy_df)
            if path: 
                generated_files['Graph 7'] = path
            print("[Supervisor Log]: Compiled Graph 7 (Engine RPM Lugging Boundaries)")

        if 8 in active_graph_ids:
            path = self.plot_graph_8_speed_penalty_ROI(tidy_df)


                # Mode A: Standard Multi-Line Comparison Chart Only
           # visualizer.plot_graph_8_speed_penalty_ROI(tidy_df, preferred_payload=35000, generate_individual_profiles=False)
    
            # Mode B: Toggle the switch to True to generate the comparison layout AND create separate files for every vehicle cut
            # visualizer.plot_graph_8_speed_penalty_ROI(tidy_df, preferred_payload=35000, generate_individual_profiles=True)



            if path: 
                generated_files['Graph 8'] = path
            print("[Supervisor Log]: Compiled Graph 8 (Windshield Time vs Fuel Dollars ROI)")

        print(f"\n--- SUCCESS: Supervisor Complete. Exported {len(generated_files)} high-resolution charts directly to your '{self.output_dir}' directory. ---")
        return generated_files


