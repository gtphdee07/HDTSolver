# Module 2 from Gemini
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import RegistryDatabase
from RegistryDatabase import TRUCK_CHASSIS_REGISTRY, ENGINE_REGISTRY, TRANSMISSION_REGISTRY, ROUTE_SCENARIO_PROFILES

class MechanicalPhysicsCalculator:
    def __init__(self):
        self.rolling_resistance_coef = 0.0062
        self.fuel_density_lbs_gal = 7.1
        self.tire_revs_per_mile = 529
        # Insert this small logic check directly inside your calculator's resolve_cruise_state method:
        #self.tire_revs_per_mile = 645 if 'Ford' in profile['chassis_key'] else 529





    def calculate_torque_at_rpm(self, engine_key, current_rpm, top_gear_active=True):
        """
        Determines exact torque output based on the engine's inflection bounds:
        Region A: Lugging zone linear decay line down to mechanical low idle.
        Region B: Flat torque plateau maximum sweet spot.
        Region C: Post-plateau hyperbolic power constant drop-off curve.
        """
        eng = ENGINE_REGISTRY[engine_key]
        peak_torque = eng['torque_top_lbft'] if top_gear_active else eng['torque_base_lbft']
        
        # Region A: Below Flat Torque Start (Lugging Decline Line)
        if current_rpm < eng['flat_torque_start_rpm']:
            if current_rpm <= eng['engine_idle_rpm']: 
                return eng['engine_idle_torque_lbft']
            slope = (peak_torque - eng['engine_idle_torque_lbft']) / (eng['flat_torque_start_rpm'] - eng['engine_idle_rpm'])
            return peak_torque - slope * (eng['flat_torque_start_rpm'] - current_rpm)
            
        # Region B: Inside Flat Torque Plateau Max
        elif eng['flat_torque_start_rpm'] <= current_rpm <= eng['flat_torque_end_rpm']:
            return peak_torque
            
        # Region C: Past Plateau towards Redline (Hyperbolic Power Constant Drop)
        else:
            if current_rpm >= eng['engine_redline_rpm']: 
                return 0
            calculated_hyperbolic_torque = (eng['peak_hp'] * 5252) / current_rpm
            return min(peak_torque, calculated_hyperbolic_torque)

    def resolve_cruise_state(self, profile):
        """
        Performs the complete energy-balance physics calculations for a 
        single velocity state under a specified terrain grade loading.
        """
        ch = TRUCK_CHASSIS_REGISTRY[profile['chassis_key']]
        eng = ENGINE_REGISTRY[profile['engine_key']]
        trans = TRANSMISSION_REGISTRY[profile['transmission_key']]
        
        speed = profile['speed_mph']
        axle = profile['axle_ratio']
        # The weight is the sum of the payload and the truck chassis
        # AI Issue: The original code incorrectly added the chassis dictionary to the weight. It should be the base chassis weight plus the payload weight.
        # it also miss spelled it, and when it fixed the missselling, it then didn't add the payload weight.
        # In debugging up to this point, I modified the code so that the "weight" variable is correctly calculated as the sum of the base tractor weight and the payload weight.
        # AI Original weigth = profile['weight_lbs'] + ch
        # AI Original weight = profile['weight_lbs']
        weight = profile['payload_weight_lbs'] + ch['base_tractor_weight_lbs']
        
        # Extract specific route vectors from our scenario profiles
        scenario = ROUTE_SCENARIO_PROFILES[profile['route']]
        grade_factor = scenario['base_grade_pct'] / 100.0
        rolling_mod = self.rolling_resistance_coef + scenario['rolling_terrain_factor']
        
        # Calculate Cruise Engine RPM assuming 12th gear is active
        top_gear_ratio = trans['gears'][max(trans['gears'].keys())]
        tire_revs_per_mile = 529 if 'Ford' not in profile['chassis_key'] else 645  # Adjust for Ford's larger tire circumference
        cruise_rpm = (speed * top_gear_ratio * axle * tire_revs_per_mile) / 60.0
        
        # Fluid power dynamics calculations (Total Drag Resistance Force Line)
        f_aero = 0.00256 * ch['aero_constant_cda'] * (speed**2)
        f_rolling = weight * rolling_mod
        f_grade = weight * grade_factor
        f_total = f_aero + f_rolling + f_grade
        
        # Apply mechanical transmission fluid friction loss modifier
        eta = 1.0 - trans['fluid_friction_loss_pct']
        hp_demand = (f_total * speed) / (375.0 * eta)
        
        # Track engine load caps to map exact BSFC deviation penalties
        max_hp_at_rpm = (self.calculate_torque_at_rpm(profile['engine_key'], cruise_rpm, True) * cruise_rpm) / 5252.0
        load_pct = hp_demand / max(1.0, max_hp_at_rpm)
        
        # Evaluate 4-wall geometric BSFC Island boundaries logic check
        bsfc = eng['best_bsfc_value']
        if not (eng['bsfc_island_low_rpm'] <= cruise_rpm <= eng['bsfc_island_high_rpm']):
            rpm_delta = max(0, cruise_rpm - eng['bsfc_island_high_rpm']) + max(0, eng['bsfc_island_low_rpm'] - cruise_rpm)
            bsfc += (rpm_delta / 100.0) * eng['outside_island_penalty_per_100rpm']
            
        # Convert total mass fuel flow rate back to standard business metrics
        gph = (hp_demand * bsfc) / self.fuel_density_lbs_gal
        mpg = speed / max(0.1, gph)
        
        return round(cruise_rpm, 0), round(mpg, 2), round(load_pct * 100, 1)


