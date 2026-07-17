# Module 2 from Gemini
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import fleet_state
#import RegistryDatabase
#from RegistryDatabase import TRUCK_CHASSIS_REGISTRY, ENGINE_REGISTRY, TRANSMISSION_REGISTRY, ROUTE_SCENARIO_PROFILES

class MechanicalPhysicsCalculator:
    def __init__(self):
        self.rolling_resistance_coef = 0.0062
        self.fuel_density_lbs_gal = 7.1
        self.tire_revs_per_mile = 529
        # Insert this small logic check directly inside your calculator's resolve_cruise_state method:
        #self.tire_revs_per_mile = 645 if 'Ford' in profile['chassis_key'] else 529



    def calculate_torque_at_rpm(self, engine_key, current_rpm, top_gear_active=True):
        """
        Calculates exact engine torque based on inflection boundaries.
        """
        eng = fleet_state.ENGINE_REGISTRY[engine_key]
        peak_torque = eng['torque_top_lbft'] if top_gear_active else eng['torque_base_lbft']
        
        if current_rpm < eng['flat_torque_start_rpm']:
            if current_rpm <= eng['engine_idle_rpm']: 
                return eng['engine_idle_torque_lbft']
            slope = (peak_torque - eng['engine_idle_torque_lbft']) / (eng['flat_torque_start_rpm'] - eng['engine_idle_rpm'])
            return peak_torque - slope * (eng['flat_torque_start_rpm'] - current_rpm)
        elif eng['flat_torque_start_rpm'] <= current_rpm <= eng['flat_torque_end_rpm']:
            return peak_torque
        else:
            if current_rpm >= eng['engine_redline_rpm']: 
                return 0
            calculated_hyperbolic_torque = (eng['peak_hp'] * 5252) / current_rpm
            return min(peak_torque, calculated_hyperbolic_torque)

    def resolve_cruise_state(self, profile):
        """
        Performs energy-balance physics calculations and dynamically solves for 
        the Speed Cushion (Delta V) and Incline Cushion (Delta Grade) shift boundaries.
        """
        ch = fleet_state.TRUCK_CHASSIS_REGISTRY[profile['chassis_key']]
        eng = fleet_state.ENGINE_REGISTRY[profile['engine_key']]
        trans = fleet_state.TRANSMISSION_REGISTRY[profile['transmission_key']]
        
        speed = profile['speed_mph']
        axle = profile['axle_ratio']
        total_w = profile['weight_lbs'] # Standard alignment check input binding
        
        scenario = fleet_state.ROUTE_SCENARIO_PROFILES[profile['route']]
        grade_factor = scenario['base_grade_pct'] / 100.0
        rolling_mod = self.rolling_resistance_coef + scenario['rolling_terrain_factor']
        
        # Adaptive tire revolutions override line for light truck rims
        tire_revs_per_mile = 645 if 'Ford' in profile['chassis_key'] else 529
        
        # Calculate Cruise Engine RPM assuming highest gear is active
        top_gear_ratio = trans['gears'][max(trans['gears'].keys())]
        cruise_rpm = (speed * top_gear_ratio * axle * tire_revs_per_mile) / 60.0
        
        # Core fluid power dynamics lines using total_w variable
        f_aero = 0.00256 * ch['aero_constant_cda'] * (speed**2)
        f_rolling = total_w * rolling_mod
        f_grade = total_w * grade_factor
        f_total = f_aero + f_rolling + f_grade
        
        eta = 1.0 - trans['fluid_friction_loss_pct']
        hp_demand = (f_total * speed) / (375.0 * eta)
        
        # Maximum potential horsepower available at this exact cruise RPM
        max_hp_at_rpm = (self.calculate_torque_at_rpm(profile['engine_key'], cruise_rpm, True) * cruise_rpm) / 5252.0
        load_pct = hp_demand / max(1.0, max_hp_at_rpm)
        
        # Dynamic BSFC evaluation
        bsfc = eng['best_bsfc_value']
        if not (eng['bsfc_island_low_rpm'] <= cruise_rpm <= eng['bsfc_island_high_rpm']):
            rpm_delta = max(0, cruise_rpm - eng['bsfc_island_high_rpm']) + max(0, eng['bsfc_island_low_rpm'] - cruise_rpm)
            bsfc += (rpm_delta / 100.0) * eng['outside_island_penalty_per_100rpm']
            
        gph = (hp_demand * bsfc) / self.fuel_density_lbs_gal
        mpg = speed / max(0.1, gph)

        # =====================================================================
        # HEADROOM MATH: METRIC 1 — SPEED DELTA CUSHION (Delta V)
        # =====================================================================
        # Find the absolute minimum speed allowed in this gear before engine drops below flat torque start
        min_stable_rpm = eng['flat_torque_start_rpm']
        v_shift_minimum = (min_stable_rpm * 60.0) / (top_gear_ratio * axle * tire_revs_per_mile)
        
        # Speed Cushion is how many MPH you can drop from current cruise before a mandatory shift
        speed_delta_cushion_mph = max(0.0, speed - v_shift_minimum)

        # =====================================================================
        # HEADROOM MATH: METRIC 2 — INCLINE DELTA CUSHION (Delta Grade)
        # =====================================================================
        # Find absolute peak available horsepower anywhere in the engine's primary map
        peak_engine_hp = eng['peak_hp']
        available_wheel_hp_max = peak_engine_hp * eta
        
        # Reserve Horsepower is your untapped power cushion at the current cruising speed
        reserve_hp = max(0.0, available_wheel_hp_max - hp_demand)
        
        # Convert Reserve HP back to force capacity (lbs) using speed parameters
        reserve_force_lbs = (reserve_hp * 375.0) / speed
        
        # Grade change cushion is how much extra incline gravity can add before matching your reserve force
        # Force_gravity_extra = Mass * Delta_Grade -> Delta_Grade = Force_reserve / Mass
        grade_delta_cushion_pct = (reserve_force_lbs / total_w) * 100.0

        return (
            round(cruise_rpm, 0), 
            round(mpg, 2), 
            round(load_pct * 100, 1), 
            round(speed_delta_cushion_mph, 1), 
            round(grade_delta_cushion_pct, 2)
        )

    def calculate_mountain_gear_and_rpm(self, profile, test_speed):
        """
        MOUNTAIN GEAR SWEEP LOGIC FOR GRAPH 7:
        Simulates transmission logic on a 6% mountain grade using total_w.
        Sequentially drops gears from 12th down to 1st to find the exact gear
        and engine RPM required to sustain the test speed without stalling.
        """
        ch = fleet_state.TRUCK_CHASSIS_REGISTRY[profile['chassis_key']]
        eng = fleet_state.ENGINE_REGISTRY[profile['engine_key']]
        trans = fleet_state.TRANSMISSION_REGISTRY[profile['transmission_key']]
        
        axle = profile['axle_ratio']
        total_w = profile['weight_lbs']
        tire_revs_per_mile = 645 if 'Ford' in profile['chassis_key'] else 529
        
        # Calculate total mountain drag force at this specific speed on a 6% grade via total_w variables
        f_aero = 0.00256 * ch['aero_constant_cda'] * (test_speed**2)
        f_rolling = total_w * self.rolling_resistance_coef
        f_grade = total_w * 0.06  # Explicit 6% mountain incline
        f_total_drag = f_aero + f_rolling + f_grade
        
        eta = 1.0 - trans['fluid_friction_loss_pct']
        hp_required = (f_total_drag * test_speed) / (375.0 * eta)
        
        total_gears = max(trans['gears'].keys())
        chosen_gear = total_gears
        calculated_rpm = 0
        
        for gear in range(total_gears, 0, -1):
            gear_ratio = trans['gears'][gear]
            test_rpm = (test_speed * gear_ratio * axle * tire_revs_per_mile) / 60.0
            
            max_torque = self.calculate_torque_at_rpm(profile['engine_key'], test_rpm, top_gear_active=(gear == total_gears))
            max_hp_available = (max_torque * test_rpm) / 5252.0
            
            if eng['flat_torque_start_rpm'] <= test_rpm <= eng['engine_redline_rpm'] and max_hp_available >= hp_required:
                chosen_gear = gear
                calculated_rpm = test_rpm
                break
            else:
                chosen_gear = gear
                calculated_rpm = test_rpm
                
        return int(chosen_gear), round(calculated_rpm, 0)

