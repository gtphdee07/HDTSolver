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
import itertools
import fleet_state  # Option B: Shares memory scope uniformly across files

class SimulationGridManager:
    @staticmethod
    def expand_and_validate_grid(user_input, passenger_cargo_allowance=500):
        """
        Ingests user requests, cross-references shared fleet state dictionaries, 
        and calculates dynamic 5% payload safety warnings and absolute tongue-weight caps.
        """
        # Read available configurations directly from the shared state module
        chassis_list = list(fleet_state.TRUCK_CHASSIS_REGISTRY.keys()) if 'ALL_VALID' in user_input['chassis'] else user_input['chassis']
        raw_permutations = []
        
        # Step 1: Run Cartesian Product to map combinations
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
        
        # Step 2: Run Phase 3 Predictive Structural Safety Audits
        for row in raw_permutations:
            ch, eng, trans, axle, trailer_gvwr, rt = row
            t_limits = fleet_state.TRANSMISSION_REGISTRY[trans]
            e_limits = fleet_state.ENGINE_REGISTRY[eng]
            ch_data = fleet_state.TRUCK_CHASSIS_REGISTRY[ch]
            
            # Since trailer_payload_lbs = RV GVWR, total weight is a direct combination sum
            total_combined_gcvw = ch_data['base_tractor_weight_lbs'] + trailer_gvwr
            
            # Skip runs that break hard mechanical boundaries (powertrain limits)
            if total_combined_gcvw > ch_data['max_chassis_gcwr_lbs']: continue
            if total_combined_gcvw > t_limits['max_gcw_limit_lbs']: continue
            if e_limits['torque_top_lbft'] > t_limits['max_input_torque_lbft']: continue
                
            # --- EVALUATE DYNAMIC SUSPENSION & PAYLOAD HEADROOM WARNINGS ---
            # Calculate remaining space available for pin weight loading
            available_payload_capacity = ch_data['max_chassis_gvwr_lbs'] - ch_data['base_tractor_weight_lbs'] - passenger_cargo_allowance
            
            # Baseline 15% fifth-wheel pin force downward push
            f_pin_15_pct = trailer_gvwr * 0.15
            remaining_payload_margin = available_payload_capacity - f_pin_15_pct
            
            # Critical threshold check: 5% of the truck's total certified load limit
            five_percent_buffer = ch_data['max_chassis_gvwr_lbs'] * 0.05
            
            # Calculate absolute max percentage before structural damage or overload triggers
            max_allowable_tongue_weight_pct = (available_payload_capacity / trailer_gvwr) * 100.0
            
            if remaining_payload_margin < five_percent_buffer:
                # Configuration remains legal but prints an instant console advisory to the user
                print(f"\n[⚠️ VEHICLE COUPLING NOTICE - {ch_data['model'].upper()}]:")
                print(f" -> Warning: Pulling a {trailer_gvwr:,} lb RV leaves less than a 5% suspension safety margin!")
                print(f" -> Pin weight at 15% consumes {f_pin_15_pct:,} lbs of your remaining {available_payload_capacity:,} lb payload capacity.")
                print(f" -> CRITICAL CEILING: A tongue weight of {max_allowable_tongue_weight_pct:.2f}% or higher will officially OVERLOAD this truck.")
                
            # Append rows safely, passing the warning values directly to your long-form data matrix
            validated_grid.append({
                'chassis_key': ch, 'engine_key': eng, 'transmission_key': trans,
                'axle_ratio': axle, 
                'trailer_payload_lbs': trailer_gvwr, 
                'weight_lbs': total_combined_gcvw,
                'route': rt,
                
                # --- STRUCURAL SCORECARD METRICS PINNED FOR LOGGING ---
                'Max_Allowable_Tongue_Pct': round(max_allowable_tongue_weight_pct, 2),
                'Payload_Margin_lbs': round(remaining_payload_margin, 0)
            })
            
        return validated_grid


