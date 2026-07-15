# Module 3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from SimulationGridManager_v3 import SimulationGridManager
import RegistryDatabase
from RegistryDatabase import TRUCK_CHASSIS_REGISTRY, ENGINE_REGISTRY, TRANSMISSION_REGISTRY, ROUTE_SCENARIO_PROFILES
import MechanicalPhysicsCalculator
import FleetDataVisualizer


class ScenarioExecutionWrapper:
    def __init__(self, physics_calculator_engine):
        # Ingests our core math calculator engine to keep operations decoupled
        self.calculator = physics_calculator_engine

    def execute_scenario_sweep_v2(self, user_hardware_input, target_scenario_keys):
        """
        Ingests user parameters, coordinates dynamic sweeps across route profiles, 
        and builds a long-formatted (Tidy) DataFrame table ready for graphing.
        """
        # Step 1: Expand and validate base hardware combinations using Module 1 logic
        validated_hardware = SimulationGridManager.expand_and_validate_grid(user_hardware_input)
        long_form_records = []

        # Step 2: Loop comprehensively over the selected Scenario Profiles
        for scenario_key in target_scenario_keys:
            scenario = ROUTE_SCENARIO_PROFILES[scenario_key]
            
            for hw in validated_hardware:
                # Match the hardware entry back to the active route scenario context
                if hw['route'] != scenario_key: continue
                    
                # Step 3: Loop directly through the specific speed list for THIS route
                for speed in scenario['speeds_to_test_mph']:
                    sim_run_profile = {
                        'chassis_key': hw['chassis_key'], 
                        'engine_key': hw['engine_key'],
                        'transmission_key': hw['transmission_key'], 
                        'axle_ratio': hw['axle_ratio'],
                        'weight_lbs': hw['weight_lbs'],  # Binds GCVW to pass to total_w in Module 2
                        'speed_mph': speed, 
                        'route': scenario_key
                    }
                    
                    # Step 4: Unpack all 5 metrics from Module 2's resolve_cruise_state
                    rpm, mpg, load, speed_cushion, grade_cushion = self.calculator.resolve_cruise_state(sim_run_profile)
                    
                    # Fetch profile tags for legible user reporting strings
                    ch_data = TRUCK_CHASSIS_REGISTRY[hw['chassis_key']]
                    eng_data = ENGINE_REGISTRY[hw['engine_key']]
                    trans_data = TRANSMISSION_REGISTRY[hw['transmission_key']]
                    
                    # Step 5: Execute dynamic mountain gear tracking checks if climbing
                    if scenario_key == 'I70_Mountain_Conqueror':
                        # Call Module 2's new gear-swept simulation function
                        gear_active, mountain_rpm = self.calculator.calculate_mountain_gear_and_rpm(sim_run_profile, speed)
                        rpm = mountain_rpm  # Overrides flat cruising RPM with real mountain gear-swept RPM
                        active_gear_label = f"Gear {gear_active}"
                    else:
                        active_gear_label = f"Gear {max(trans_data['gears'].keys())}" # Standard flat top gear (10 or 12)

                    # Step 6: Process business performance kinematics and safety flags
                    accel_mod = (hw['weight_lbs'] / 45000.0) * (2.64 / hw['axle_ratio'])
                    hp_mod = 450.0 / eng_data['peak_hp']
                    
                    t_0_50 = round(35.0 * accel_mod * hp_mod, 1)
                    t_pass = round(11.5 * accel_mod * hp_mod, 1)
                    t_hill_start = round(18.2 * accel_mod * hp_mod * (1.0 + scenario['base_grade_pct']/6.0), 1)
                    
                    # Step 7: Dynamic braking force balance engine safety check
                    speed_descent = 45.0
                    grade_pct = scenario['base_grade_pct'] / 100.0
                    
                    if grade_pct > 0:
                        f_gravity = hw['weight_lbs'] * grade_pct
                        f_rolling = hw['weight_lbs'] * 0.0062
                        f_aero = 0.00256 * ch_data['aero_constant_cda'] * (speed_descent ** 2)
                        
                        f_net_descent = max(0.0, f_gravity - f_rolling - f_aero)
                        hp_braking_required = (f_net_descent * speed_descent) / 375.0
                        
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

                    # Step 8: Calculate absolute max climbing speed limit for Graph 2
                    eta_trans = 1.0 - trans_data['fluid_friction_loss_pct']
                    v_max_6pct = (eng_data['peak_hp'] * eta_trans * 375.0) / (hw['weight_lbs'] * (0.06 + 0.0062))
                    v_max_6pct = min(75.0, round(v_max_6pct, 1))

                    # Step 9: Compile rows into the master long-form schema
                    tidy_row = {
                        'Truck_Model': ch_data['model'],
                        'Engine_Series': eng_data['engine_family'],
                        'Transmission': trans_data['model'],
                        'Axle_Ratio': hw['axle_ratio'],
                        'Trailer_Payload_lbs': hw['trailer_payload_lbs'], # Re-aligned separate payload tracker
                        'Weight_lbs': hw['weight_lbs'],                  # Re-aligned total combination GCVW
                        'Route_Scenario': scenario_key,
                        'Speed_MPH': speed,
                        'Active_Gear': active_gear_label,
                        'Engine_Cruise_RPM': rpm,
                        'Calculated_MPG': mpg,
                        'Engine_Load_Pct': load,
                        
                        # --- HEADROOM CUSHION DATA COLUMNS BOUND ---
                        'Speed_Cushion_MPH': speed_cushion,
                        'Grade_Cushion_Pct': grade_cushion,
                        
                        'Accel_0_50_s': t_0_50,
                        'Passing_45_65_s': t_pass,
                        'Mountain_Start_0_30_s': t_hill_start if scenario['base_grade_pct'] > 0 else "N/A",
                        'Downhill_Braking_Safety': brake_status,
                        'Max_Speed_6pct_Grade_MPH': v_max_6pct,
                        'Downhill_Req_Braking_HP': round(hp_braking_required, 1)
                    }
                    long_form_records.append(tidy_row)
                    
        return pd.DataFrame(long_form_records)
    def execute_scenario_sweep(self, user_hardware_input, target_scenario_keys):
        """
        Ingests user parameters, coordinates dynamic sweeps across route profiles, 
        and builds a long-formatted (Tidy) DataFrame table ready for graphing.
        """
        validated_hardware = SimulationGridManager.expand_and_validate_grid(user_hardware_input)
        long_form_records = []

        for scenario_key in target_scenario_keys:
            scenario = ROUTE_SCENARIO_PROFILES[scenario_key]
            
            for hw in validated_hardware:
                if hw['route'] != scenario_key: continue
                
                ch_data = TRUCK_CHASSIS_REGISTRY[hw['chassis_key']]
                eng_data = ENGINE_REGISTRY[hw['engine_key']]
                trans_data = TRANSMISSION_REGISTRY[hw['transmission_key']]
                
                # Calculate absolute max climbing speed limit up a 6% grade for this specific configuration
                eta_trans = 1.0 - trans_data['fluid_friction_loss_pct']
                v_max_6pct = (eng_data['peak_hp'] * eta_trans * 375.0) / (hw['weight_lbs'] * (0.06 + 0.0062))
                v_max_6pct = min(75.0, round(v_max_6pct, 1))

                # =====================================================================
                # DYNAMIC CORRECTIONS: MOUNTAIN CORRIDOR SPEED OVERRIDE
                # =====================================================================
                if scenario_key == 'I70_Mountain_Conqueror':
                    # Instead of a short 3-point cruise list, run a high-resolution, dense sweep
                    # starting from a 15 MPH crawl up to the truck's exact maximum capability limit
                    if v_max_6pct > 15:
                        speeds_to_execute = list(np.arange(15.0, v_max_6pct + 0.1, 2.0))
                        # Explicitly append the absolute maximum velocity point to finish the line sweep
                        if speeds_to_execute[-1] != v_max_6pct:
                            speeds_to_execute.append(v_max_6pct)
                    else:
                        # Fallback case if a truck is so heavily overloaded it cannot even sustain 15 MPH
                        speeds_to_execute = [v_max_6pct]
                else:
                    # Flat/Rolling terrain corridors continue using the user's standard cruise list
                    speeds_to_execute = scenario['speeds_to_test_mph']

                # =====================================================================
                # CORE AUTOMATED CALCULATION MATRIX LOOP
                # =====================================================================
                for speed in speeds_to_execute:
                    sim_run_profile = {
                        'chassis_key': hw['chassis_key'], 'engine_key': hw['engine_key'],
                        'transmission_key': hw['transmission_key'], 'axle_ratio': hw['axle_ratio'],
                        'weight_lbs': hw['weight_lbs'], 'speed_mph': speed, 'route': scenario_key
                    }
                    
                    # Unpack standard state variables from Module 2
                    rpm, mpg, load, speed_cushion, grade_cushion = self.calculator.resolve_cruise_state(sim_run_profile)
                    
                    if scenario_key == 'I70_Mountain_Conqueror':
                        # Execute our dynamic gear-swept mountain simulator function
                        gear_active, mountain_rpm = self.calculator.calculate_mountain_gear_and_rpm(sim_run_profile, speed)
                        rpm = mountain_rpm  # Lock RPM to real-world gear results
                        active_gear_label = f"Gear {gear_active}"
                        load = 100.0 if speed == v_max_6pct else min(100.0, load)
                    else:
                        active_gear_label = f"Gear {max(trans_data['gears'].keys())}"

                    # Kinematic and Braking Calculations
                    accel_mod = (hw['weight_lbs'] / 45000.0) * (2.64 / hw['axle_ratio'])
                    hp_mod = 450.0 / eng_data['peak_hp']
                    
                    t_0_50 = round(35.0 * accel_mod * hp_mod, 1)
                    t_pass = round(11.5 * accel_mod * hp_mod, 1)
                    t_hill_start = round(18.2 * accel_mod * hp_mod * (1.0 + scenario['base_grade_pct']/6.0), 1)
                    
                    speed_descent = 45.0
                    grade_pct = scenario['base_grade_pct'] / 100.0
                    if grade_pct > 0:
                        f_gravity = hw['weight_lbs'] * grade_pct
                        f_rolling = hw['weight_lbs'] * 0.0062
                        f_aero = 0.00256 * ch_data['aero_constant_cda'] * (speed_descent ** 2)
                        hp_braking_required = max(0.0, (f_gravity - f_rolling - f_aero) * speed_descent / 375.0)
                        
                        safety_margin = eng_data['max_braking_hp'] - hp_braking_required
                        brake_status = "MAX SAFETY" if safety_margin > 50 else ("SAFE (STABLE)" if safety_margin >= 0 else "CRITICAL WARNING")
                    else:
                        hp_braking_required = 0.0
                        brake_status = "N/A"
                    
                    tidy_row = {
                        'Truck_Model': ch_data['model'], 'Engine_Series': eng_data['engine_family'],
                        'Transmission': trans_data['model'], 'Axle_Ratio': hw['axle_ratio'],
                        'Trailer_Payload_lbs': hw['trailer_payload_lbs'], 'Weight_lbs': hw['weight_lbs'],
                        'Route_Scenario': scenario_key, 'Speed_MPH': round(speed, 1), 'Active_Gear': active_gear_label,
                        'Engine_Cruise_RPM': rpm, 'Calculated_MPG': mpg, 'Engine_Load_Pct': load,
                        'Speed_Cushion_MPH': speed_cushion, 'Grade_Cushion_Pct': grade_cushion,
                        'Accel_0_50_s': t_0_50, 'Passing_45_65_s': t_pass, 
                        'Mountain_Start_0_30_s': t_hill_start if scenario['base_grade_pct'] > 0 else "N/A",
                        'Downhill_Braking_Safety': brake_status, 'Max_Speed_6pct_Grade_MPH': v_max_6pct,
                        'Downhill_Req_Braking_HP': round(hp_braking_required, 1)
                    }
                    long_form_records.append(tidy_row)
                    
        return pd.DataFrame(long_form_records)



    @staticmethod
    def export_to_multi_tab_excel(tidy_dataframe, file_name="Executive_Fleet_Report.xlsx"):
        """
        Reshapes the tidy dataframe into structured, decision-maker tabs 
        and saves them out as an integrated Microsoft Excel workbook.
        """
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            # --- TAB 1: EXECUTIVE OVERVIEW (Isolates standard 65 MPH operations) ---
            exec_brief = tidy_dataframe[tidy_dataframe['Speed_MPH'] == 65][[
                'Truck_Model', 'Engine_Series', 'Axle_Ratio', 'Trailer_Payload_lbs', 
                'Route_Scenario', 'Calculated_MPG', 'Engine_Cruise_RPM', 'Downhill_Braking_Safety'
            ]]
            exec_brief.to_excel(writer, sheet_name='Executive Overview', index=False)
            
            # --- TAB 2: FUEL EFFICIENCY COMPARISON MATRIX ---
            # Pivots tidy rows into distinct side-by-side columns for quick speed comparisons
            mpg_matrix = tidy_dataframe.pivot_table(
                index=['Truck_Model', 'Engine_Series', 'Axle_Ratio', 'Trailer_Payload_lbs'],
                columns=['Route_Scenario', 'Speed_MPH'],
                values='Calculated_MPG'
            )
            mpg_matrix.to_excel(writer, sheet_name='MPG Sensitivity Matrix')
            
            # --- TAB 3: PERFORMANCE TIMINGS SCORECARD ---
            safety_scorecard = tidy_dataframe[[
                'Truck_Model', 'Engine_Series', 'Trailer_Payload_lbs', 'Route_Scenario',
                'Accel_0_50_s', 'Passing_45_65_s', 'Mountain_Start_0_30_s', 'Downhill_Braking_Safety'
            ]].drop_duplicates()
            safety_scorecard.to_excel(writer, sheet_name='Safety & Performance', index=False)
            
            # --- TAB 4: COMPLETE SIMULATION LOGS ---
            tidy_dataframe.to_excel(writer, sheet_name='Raw Data Archive', index=False)
            
        print(f"\nExcel Exporter: Reshaped data structure and successfully compiled '{file_name}'")

