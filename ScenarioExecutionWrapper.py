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
import ExcelFleetDatabase


# =====================================================================
# MODULE 3: AUTOMATION LOOP WRAPPER (SELF-CORRECTING MOUNTAIN SWEEPS)
# =====================================================================
class ScenarioExecutionWrapper:
    def __init__(self, physics_calculator_engine):
        self.calculator = physics_calculator_engine

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
                
                # Calculate absolute max climbing speed limit up a 6% grade for this config
                eta_trans = 1.0 - trans_data['fluid_friction_loss_pct']
                v_max_6pct = (eng_data['peak_hp'] * eta_trans * 375.0) / (hw['weight_lbs'] * (0.06 + 0.0062))
                v_max_6pct = min(75.0, round(v_max_6pct, 1))

                # Inject dense 2 MPH resolution sweeps inside the mountain pass boundaries
                if scenario_key == 'I70_Mountain_Conqueror':
                    if v_max_6pct > 15:
                        speeds_to_execute = list(np.arange(15.0, v_max_6pct + 0.1, 2.0))
                        if speeds_to_execute[-1] != v_max_6pct: speeds_to_execute.append(v_max_6pct)
                    else:
                        speeds_to_execute = [v_max_6pct]
                else:
                    speeds_to_execute = scenario['speeds_to_test_mph']

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
                        rpm = mountain_rpm
                        active_gear_label = f"Gear {gear_active}"
                        load = 100.0 if speed == v_max_6pct else min(100.0, load)
                    else:
                        active_gear_label = f"Gear {max(trans_data['gears'].keys())}"

                    # Kinematic modifiers based on separated weight profiles
                    accel_mod = (hw['weight_lbs'] / 45000.0) * (2.64 / hw['axle_ratio'])
                    hp_mod = 450.0 / eng_data['peak_hp']
                    
                    t_0_50 = round(35.0 * accel_mod * hp_mod, 1)
                    t_pass = round(11.5 * accel_mod * hp_mod, 1)
                    t_hill_start = round(18.2 * accel_mod * hp_mod * (1.0 + scenario['base_grade_pct']/6.0), 1)
                    
                    # Dynamic downhill force balance safety check
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
            exec_brief = tidy_dataframe[tidy_dataframe['Speed_MPH'] == 65][[
                'Truck_Model', 'Engine_Series', 'Axle_Ratio', 'Weight_lbs', 
                'Route_Scenario', 'Calculated_MPG', 'Engine_Cruise_RPM', 'Downhill_Braking_Safety'
            ]]
            exec_brief.to_excel(writer, sheet_name='Executive Overview', index=False)
            
            try:
                mpg_matrix = tidy_dataframe.pivot_table(
                    index=['Truck_Model', 'Engine_Series', 'Axle_Ratio', 'Weight_lbs'],
                    columns=['Route_Scenario', 'Speed_MPH'], values='Calculated_MPG'
                )
                mpg_matrix.to_excel(writer, sheet_name='MPG Sensitivity Matrix')
            except Exception:
                pass
            tidy_dataframe.to_excel(writer, sheet_name='Raw Data Archive', index=False)
            
        print(f"\nExcel Exporter: Reshaped data structure and successfully compiled '{file_name}'")

