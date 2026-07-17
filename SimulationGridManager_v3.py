# Module 1
import pandas as pd
import numpy as np
import itertools
import json
import os
import fleet_state
#import RegistryDatabase   
#from RegistryDatabase import TRUCK_CHASSIS_REGISTRY, ENGINE_REGISTRY, TRANSMISSION_REGISTRY

# 
# =====================================================================
# MODULE 1: GRID EXPANSION MANAGER
# =====================================================================


# =====================================================================
# MODULE 1: COMPLIANCE INTEGRITY & STRUCTURAL OVERLOAD GATEKEEPER
# =====================================================================
class SimulationGridManager:
    @staticmethod
    def expand_and_validate_grid(user_input, passenger_cargo_allowance=500):
        """
        Ingests configuration parameters, models 15% tongue weight dynamics,
        and runs strict structural manufacturing safety checks prior to physics loops.
        """
        chassis_list = list(fleet_state.TRUCK_CHASSIS_REGISTRY.keys()) if 'ALL_VALID' in user_input['chassis'] else user_input['chassis']
        raw_permutations = []
        
        # Step 1: Execute Cartesian Product mapping
        for ch_key in chassis_list:
            ch_data = fleet_state.TRUCK_CHASSIS_REGISTRY[ch_key]
            engines = ch_data['valid_engines'] if 'ALL_VALID' in user_input['engine'] else [e for e in user_input['engine'] if e in ch_data['valid_engines']]
            transmissions = ch_data['valid_transmissions'] if 'ALL_VALID' in user_input['transmission'] else [t for t in user_input['transmission'] if t in ch_data['valid_transmissions']]
            axles = ch_data['valid_rear_end_ratios'] if 'ALL_VALID' in user_input['axle_ratio'] else [a for a in user_input['axle_ratio'] if a in ch_data['valid_rear_end_ratios']]
            
            payloads = user_input['trailer_payload_lbs']
            routes = user_input['route_corridor']
            
            chassis_grid = list(itertools.product([ch_key], engines, transmissions, axles, payloads, routes))
            raw_permutations.extend(chassis_grid)
            
        validated_grid = []
        rejected_count = 0
        
        # Step 2: Run Phase 3 Structural Safety Audits
        for row in raw_permutations:
            ch, eng, trans, axle, p_w, rt = row
            t_limits = fleet_state.TRANSMISSION_REGISTRY[trans]
            e_limits = fleet_state.ENGINE_REGISTRY[eng]
            ch_data = fleet_state.TRUCK_CHASSIS_REGISTRY[ch]
            
            # Dynamic Empty Trailer Weight Model: scales with the cargo class size
            # Light payloads assume consumer goosenecks, heavy payloads assume commercial chassis frames
            empty_trailer_weight = 7500 if p_w <= 25000 else 12500
            
            # Compute operational kinematics mass boundaries
            total_trailer_weight = p_w + empty_trailer_weight
            calculated_pin_weight = total_trailer_weight * 0.15 # 15% tongue-weight constant rule
            
            calculated_truck_gvw = ch_data['base_tractor_weight_lbs'] + calculated_pin_weight + passenger_cargo_allowance
            total_combined_gcvw = ch_data['base_tractor_weight_lbs'] + total_trailer_weight

            # --- RUN CRITICAL STRUCTURAL SAFETY TRIPS ---
            
            # Check 1: Structural Truck Axle/Frame Payload Overload (GVWR)
            if calculated_truck_gvw > ch_data['max_chassis_gvwr_lbs']:
                rejected_count += 1
                continue # Gracefully drop the configuration from the execution loop
                
            # Check 2: Powertrain Towing Capability Limit (GCWR)
            if total_combined_gcvw > ch_data['max_chassis_gcwr_lbs']:
                rejected_count += 1
                continue
                
            # Check 3: Transmission Structural Warranty Cap
            if total_combined_gcvw > t_limits['max_gcw_limit_lbs']:
                rejected_count += 1
                continue
                
            # Check 4: Engine-to-Gearbox Input Torque Ceiling
            if e_limits['torque_top_lbft'] > t_limits['max_input_torque_lbft']: 
                rejected_count += 1
                continue
                
            # If all checks pass cleanly, append the validated row package to the queue
            validated_grid.append({
                'chassis_key': ch, 'engine_key': eng, 'transmission_key': trans,
                'axle_ratio': axle, 
                'trailer_payload_lbs': p_w, 
                'weight_lbs': total_combined_gcvw, # Maps GCVW straight to total_w in Module 2
                'route': rt
            })
            
        print(f"Safety Gatekeeper: Audited permutations. Approved {len(validated_grid)} legal configurations, filtered out {rejected_count} overloaded safety violations.")
        return validated_grid

