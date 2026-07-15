import pandas as pd
import numpy as np
import itertools
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure local environment has dependencies: pip install pandas numpy matplotlib seaborn openpyxl

# =====================================================================
# DYNAMIC EXTERNAL REGISTRY DATABASE LOADER
# =====================================================================
class RegistryDatabase:
    def __init__(self, registry_dir="registries"):
        self.directory = registry_dir
        self.transmissions = {}
        self.engines = {}
        self.trucks = {}

    def load_database(self):
        try:
            trans_path = os.path.join(self.directory, "transmissions.json")
            engine_path = os.path.join(self.directory, "engines.json")
            trucks_path = os.path.join(self.directory, "trucks.json")

            with open(trans_path, "r") as f:
                raw_trans = json.load(f)
                self.transmissions = {
                    k: {**v, 'gears': {int(g_k): g_v for g_k, g_v in v['gears'].items()}}
                    for k, v in raw_trans.items()
                }

            with open(engine_path, "r") as f:
                self.engines = json.load(f)

            with open(trucks_path, "r") as f:
                self.trucks = json.load(f)

            self._audit_structural_integrity()
            print("Database Engine: JSON registries loaded and verified with 0 anomalies.")
            
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"\n[Database Error]: System could not locate a required JSON registry file.\n"
                f"Please ensure you created a '{self.directory}/' sub-folder containing "
                f"transmissions.json, engines.json, and trucks.json exactly.\nDetails: {e}"
            )
        except json.JSONDecodeError as e:
            raise ValueError(
                f"\n[JSON Syntax Error]: A text file contains an illegal format character.\nDetails: {e}"
            )

    def _audit_structural_integrity(self):
        mandatory_truck_fields = ['base_tractor_weight_lbs', 'aero_constant_cda', 'valid_engines', 'valid_transmissions']
        for truck_key, specs in self.trucks.items():
            for field in mandatory_truck_fields:
                if field not in specs:
                    raise KeyError(f"Registry Validation Failure: '{truck_key}' is missing the mandatory '{field}' field!")
            for eng_key in specs['valid_engines']:
                if eng_key not in self.engines:
                    raise ValueError(f"Integrity Link Error: Truck '{truck_key}' references engine '{eng_key}', missing inside engines.json!")
            for trans_key in specs['valid_transmissions']:
                if trans_key not in self.transmissions:
                    raise ValueError(f"Integrity Link Error: Truck '{truck_key}' references transmission '{trans_key}', missing inside transmissions.json!")

# Initialize and fill database variables
db_loader = RegistryDatabase(registry_dir="registries")
db_loader.load_database()

TRANSMISSION_REGISTRY = db_loader.transmissions
ENGINE_REGISTRY = db_loader.engines
TRUCK_CHASSIS_REGISTRY = db_loader.trucks

ROUTE_SCENARIO_PROFILES = {
    'I95_Fuel_Slasher': {
        'description': 'Flat long-haul corridor', 'base_grade_pct': 0.0, 'rolling_terrain_factor': 0.0,
        'speeds_to_test_mph':, 'focus_metric': 'Aerodynamic Fuel Optimization'
    },
    'I40_Midwest_Rhythm': {
        'description': 'Rolling hills corridor', 'base_grade_pct': 0.0, 'rolling_terrain_factor': 0.02, 
        'speeds_to_test_mph':, 'focus_metric': 'Gear Hunting & Shift Frequency Index'
    },
    'I70_Mountain_Conqueror': {
        'description': 'Severe mountain grades', 'base_grade_pct': 6.0, 'rolling_terrain_factor': 0.0,
        'speeds_to_test_mph':, 'focus_metric': 'Peak Gradeability & Downhill Braking Safety'
    }
}

# =====================================================================
# MODULE 1: GRID EXPANSION MANAGER
# =====================================================================
class SimulationGridManager:
    @staticmethod
    def expand_and_validate_grid(user_input):
        chassis_list = list(TRUCK_CHASSIS_REGISTRY.keys()) if 'ALL_VALID' in user_input['chassis'] else user_input['chassis']
        raw_permutations = []
        
        for ch_key in chassis_list:
            ch_data = TRUCK_CHASSIS_REGISTRY[ch_key]
            engines = ch_data['valid_engines'] if 'ALL_VALID' in user_input['engine'] else [e for e in user_input['engine'] if e in ch_data['valid_engines']]
            transmissions = ch_data['valid_transmissions'] if 'ALL_VALID' in user_input['transmission'] else [t for t in user_input['transmission'] if t in ch_data['valid_transmissions']]
            axles = ch_data['valid_rear_end_ratios'] if 'ALL_VALID' in user_input['axle_ratio'] else [a for a in user_input['axle_ratio'] if a in ch_data['valid_rear_end_ratios']]
            
            payloads = user_input['trailer_payload_lbs']
            routes = user_input['route_corridor']
            
            chassis_grid = list(itertools.product([ch_key], engines, transmissions, axles, payloads, routes))
            raw_permutations.extend(chassis_grid)
            
        validated_grid = []
        for row in raw_permutations:
            ch, eng, trans, axle, p_w, rt = row
            t_limits = TRANSMISSION_REGISTRY[trans]
            e_limits = ENGINE_REGISTRY[eng]
            ch_data = TRUCK_CHASSIS_REGISTRY[ch]
            
            total_w = ch_data['base_tractor_weight_lbs'] + p_w
            
            if e_limits['torque_top_lbft'] > t_limits['max_input_torque_lbft']: continue
            if total_w > t_limits['max_gcw_limit_lbs']: continue
                
            validated_grid.append({
                'chassis_key': ch, 'engine_key': eng, 'transmission_key': trans,
                'axle_ratio': axle, 'trailer_payload_lbs': p_w, 'weight_lbs': total_w, 'route': rt
            })
            
        print(f"Grid Processor: Ingested constraints and verified {len(validated_grid)} build combinations.")
        return validated_grid

# =====================================================================
# MODULE 2: MECHANICAL PHYSICS CALCULATOR ENGINE
# =====================================================================
class MechanicalPhysicsCalculator:
    def __init__(self):
        self.rolling_resistance_coef = 0.0062
        self.fuel_density_lbs_gal = 7.1

    def calculate_torque_at_rpm(self, engine_key, current_rpm, top_gear_active=True):
        eng = ENGINE_REGISTRY[engine_key]
        peak_torque = eng['torque_top_lbft'] if top_gear_active else eng['torque_base_lbft']
        
        if current_rpm < eng['flat_torque_start_rpm']:
            if current_rpm <= eng['engine_idle_rpm']: return eng['engine_idle_torque_lbft']
            slope = (peak_torque - eng['engine_idle_torque_lbft']) / (eng['flat_torque_start_rpm'] - eng['engine_idle_rpm'])
            return peak_torque - slope * (eng['flat_torque_start_rpm'] - current_rpm)
        elif eng['flat_torque_start_rpm'] <= current_rpm <= eng['flat_torque_end_rpm']:
            return peak_torque
        else:
            if current_rpm >= eng['engine_redline_rpm']: return 0
            calculated_hyperbolic_torque = (eng['peak_hp'] * 5252) / current_rpm
            return min(peak_torque, calculated_hyperbolic_torque)

    def resolve_cruise_state(self, profile):
        ch = TRUCK_CHASSIS_REGISTRY[profile['chassis_key']]
        eng = ENGINE_REGISTRY[profile['engine_key']]
        trans = TRANSMISSION_REGISTRY[profile['transmission_key']]
        
        speed = profile['speed_mph']
        axle = profile['axle_ratio']
        total_w = profile['weight_lbs']
        
        scenario = ROUTE_SCENARIO_PROFILES[profile['route']]
        grade_factor = scenario['base_grade_pct'] / 100.0
        rolling_mod = self.rolling_resistance_coef + scenario['rolling_terrain_factor']
        
        # Adaptive tire revolutions override line for light truck rims
        tire_revs = 645 if 'Ford' in profile['chassis_key'] else 529
        
        top_gear_ratio = trans['gears'][max(trans['gears'].keys())]
        cruise_rpm = (speed * top_gear_ratio * axle * tire_revs) / 60.0
        
        f_aero = 0.00256 * ch['aero_constant_cda'] * (speed**2)
        f_rolling = total_w * rolling_mod
        f_grade = total_w * grade_factor
        f_total = f_aero + f_rolling + f_grade
        
        eta = 1.0 - trans['fluid_friction_loss_pct']
        hp_demand = (f_total * speed) / (375.0 * eta)
        
        max_hp_at_rpm = (self.calculate_torque_at_rpm(profile['engine_key'], cruise_rpm, True) * cruise_rpm) / 5252.0
        load_pct = hp_demand / max(1.0, max_hp_at_rpm)
        
        bsfc = eng['best_bsfc_value']
        if not (eng['bsfc_island_low_rpm'] <= cruise_rpm <= eng['bsfc_island_high_rpm']):
            rpm_delta = max(0, cruise_rpm - eng['bsfc_island_high_rpm']) + max(0, eng['bsfc_island_low_rpm'] - cruise_rpm)
            bsfc += (rpm_delta / 100.0) * eng['outside_island_penalty_per_100rpm']
            
        gph = (hp_demand * bsfc) / self.fuel_density_lbs_gal
        mpg = speed / max(0.1, gph)
        
        return round(cruise_rpm, 0), round(mpg, 2), round(load_pct * 100, 1)
# =====================================================================
# MODULE 3: AUTOMATION EXECUTION WRAPPER & RESHAPER
# =====================================================================

class ScenarioExecutionWrapper:
    def __init__(self, physics_calculator_engine):
        self.calculator = physics_calculator_engine

    def execute_scenario_sweep(self, user_hardware_input, target_scenario_keys):
        validated_hardware = SimulationGridManager.expand_and_validate_grid(user_hardware_input)
        long_form_records = []

        for scenario_key in target_scenario_keys:
            scenario = ROUTE_SCENARIO_PROFILES[scenario_key]
            
            for hw in validated_hardware:
                if hw['route'] != scenario_key: continue
                    
                for speed in scenario['speeds_to_test_mph']:
                    sim_run_profile = {
                        'chassis_key': hw['chassis_key'], 
                        'engine_key': hw['engine_key'],
                        'transmission_key': hw['transmission_key'], 
                        'axle_ratio': hw['axle_ratio'],
                        'weight_lbs': hw['weight_lbs'], 
                        'speed_mph': speed, 
                        'route': scenario_key
                    }
                    
                    rpm, mpg, load = self.calculator.resolve_cruise_state(sim_run_profile)
                    
                    ch_data = TRUCK_CHASSIS_REGISTRY[hw['chassis_key']]
                    eng_data = ENGINE_REGISTRY[hw['engine_key']]
                    trans_data = TRANSMISSION_REGISTRY[hw['transmission_key']]
                    
                    # Core physics expansion line solving uphill top speeds
                    eta_trans = 1.0 - trans_data['fluid_friction_loss_pct']
                    v_max_6pct = (eng_data['peak_hp'] * eta_trans * 375.0) / (hw['weight_lbs'] * (0.06 + 0.0062))
                    v_max_6pct = min(75.0, round(v_max_6pct, 1))

                    accel_mod = (hw['weight_lbs'] / 45000.0) * (2.64 / hw['axle_ratio'])
                    hp_mod = 450.0 / eng_data['peak_hp']
                    
                    t_0_50 = round(35.0 * accel_mod * hp_mod, 1)
                    t_pass = round(11.5 * accel_mod * hp_mod, 1)
                    t_hill_start = round(18.2 * accel_mod * hp_mod * (1.0 + scenario['base_grade_pct']/6.0), 1)
                    
                    # Dynamic braking safety engine check
                    speed_descent = 45.0
                    grade_pct = scenario['base_grade_pct'] / 100.0
                    if grade_pct > 0:
                        f_gravity = hw['weight_lbs'] * grade_pct
                        f_rolling = hw['weight_lbs'] * 0.0062
                        f_aero = 0.00256 * ch_data['aero_constant_cda'] * (speed_descent ** 2)
                        hp_braking_required = max(0.0, (f_gravity - f_rolling - f_aero) * speed_descent / 375.0)
                        
                        safety_margin = eng_data['max_braking_hp'] - hp_braking_required
                        if safety_margin > 50:
                            brake_status = "MAX SAFETY"
                        elif safety_margin >= 0:
                            brake_status = "SAFE (STABLE)"
                        else:
                            brake_status = "CRITICAL WARNING"
                    else:
                        hp_braking_required = 0.0
                        brake_status = "N/A"
                    
                    tidy_row = {
                        'Truck_Model': ch_data['model'], 
                        'Engine_Series': eng_data['engine_family'],
                        'Transmission': trans_data['model'], 
                        'Axle_Ratio': hw['axle_ratio'],
                        'Trailer_Payload_lbs': hw['trailer_payload_lbs'], 
                        'Weight_lbs': hw['weight_lbs'], 
                        'Route_Scenario': scenario_key, 
                        'Speed_MPH': speed, 
                        'Engine_Cruise_RPM': rpm,
                        'Calculated_MPG': mpg, 
                        'Engine_Load_Pct': load, 
                        'Accel_0_50_s': t_0_50,
                        'Passing_45_65_s': t_pass, 
                        'Mountain_Start_0_30_s': t_hill_start if scenario['base_grade_pct'] > 0 else "N/A",
                        'Downhill_Braking_Safety': brake_status, 
                        'Max_Speed_6pct_Grade_MPH': v_max_6pct,
                        'Downhill_Req_Braking_HP': round(hp_braking_required, 1)
                    }
                    long_form_records.append(tidy_row)
                    
        return pd.DataFrame(long_form_records)

    @staticmethod
    def export_to_multi_tab_excel(tidy_dataframe, file_name="Executive_Fleet_Report.xlsx"):
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            exec_brief = tidy_dataframe[tidy_dataframe['Speed_MPH'] == 65][[
                'Truck_Model', 'Engine_Series', 'Axle_Ratio', 'Weight_lbs', 
                'Route_Scenario', 'Calculated_MPG', 'Engine_Cruise_RPM', 'Downhill_Braking_Safety'
            ]]
            exec_brief.to_excel(writer, sheet_name='Executive Overview', index=False)
            
            mpg_matrix = tidy_dataframe.pivot_table(
                index=['Truck_Model', 'Engine_Series', 'Axle_Ratio', 'Weight_lbs'],
                columns=['Route_Scenario', 'Speed_MPH'], 
                values='Calculated_MPG'
            )
            mpg_matrix.to_excel(writer, sheet_name='MPG Sensitivity Matrix')
            
            tidy_dataframe.to_excel(writer, sheet_name='Raw Data Archive', index=False)
            
        print(f"\nExcel Exporter: Reshaped data structure and successfully compiled '{file_name}'")

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
# PIPELINE EXECUTION TRIGGER
# =====================================================================
if __name__ == '__main__':
    physics_calc = MechanicalPhysicsCalculator()
    wrapper_engine = ScenarioExecutionWrapper(physics_calc)

    # Ingest inputs supporting all Wave 1 scenarios and the Ford pickup keys
    user_request = {
        'chassis': ['Volvo_VNL_860', 'Kenworth_T680_NextGen', 'Ford_F450_Pickup'],
        'engine': ['ALL_VALID'],
        'transmission': ['ALL_VALID'],
        'axle_ratio': ['ALL_VALID'],
        'trailer_payload_lbs':[25000, 35000], 
        'route_corridor': ['I95_Fuel_Slasher', 'I40_Midwest_Rhythm', 'I70_Mountain_Conqueror']
    }

    print("--- STARTING COGNITIVE FLEET SIMULATION FULL RUN SWEEP ---")
    tidy_df = wrapper_engine.execute_scenario_sweep(
        user_request, ['I95_Fuel_Slasher', 'I40_Midwest_Rhythm', 'I70_Mountain_Conqueror']
    )

    print("\n--- SAMPLE SIMULATION RESULTS TABLE MATRIX ---")
    print(tidy_df[['Truck_Model', 'Axle_Ratio', 'Trailer_Payload_lbs', 'Route_Scenario', 'Speed_MPH', 'Calculated_MPG']].head(15))

    # Push to Excel Tabs Archive
    wrapper_engine.export_to_multi_tab_excel(tidy_df, "Fleet_Executive_Decision_Matrix.xlsx")

    # Instantiate our graphics supervisor engine class to render all 8 Wave 1 charts to disk
    visualizer = FleetDataVisualizer(output_dir="executive_presentation_charts", palette="Set1")
    visualizer.generate_executive_visual_report(tidy_df, active_graph_ids=[1, 2, 3, 4, 5, 6, 7, 8])
