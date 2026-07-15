# Module 1
import pandas as pd
import numpy as np
import itertools
import json
import os
import RegistryDatabase   
from RegistryDatabase import TRUCK_CHASSIS_REGISTRY, ENGINE_REGISTRY, TRANSMISSION_REGISTRY

# 
# =====================================================================
# MODULE 1: GRID EXPANSION MANAGER
# =====================================================================


class SimulationGridManager:
    @staticmethod
    def expand_and_validate_grid(user_input):
        chassis_list = (
            list(TRUCK_CHASSIS_REGISTRY.keys())
            if "ALL_VALID" in user_input["chassis"]
            else user_input["chassis"]
        )
        raw_permutations = []

        for ch_key in chassis_list:
            ch_data = TRUCK_CHASSIS_REGISTRY[ch_key]

            engines = (
                ch_data["valid_engines"]
                if "ALL_VALID" in user_input["engine"]
                else [e for e in user_input["engine"] if e in ch_data["valid_engines"]]
            )
            transmissions = (
                ch_data["valid_transmissions"]
                if "ALL_VALID" in user_input["transmission"]
                else [
                    t
                    for t in user_input["transmission"]
                    if t in ch_data["valid_transmissions"]
                ]
            )
            axles = (
                ch_data["valid_rear_end_ratios"]
                if "ALL_VALID" in user_input["axle_ratio"]
                else [
                    a
                    for a in user_input["axle_ratio"]
                    if a in ch_data["valid_rear_end_ratios"]
                ]
            )

            payload_weights = user_input["payload_weight_lbs"]
            routes = user_input["route_corridor"]

            chassis_grid = list(
                itertools.product(
                    [ch_key], engines, transmissions, axles, payload_weights, routes
                )
            )
            raw_permutations.extend(chassis_grid)

        validated_grid = []
        for row in raw_permutations:
            ch, eng, trans, axle, payload_weight, rt = row
            t_limits = TRANSMISSION_REGISTRY[trans]
            e_limits = ENGINE_REGISTRY[eng]

            if e_limits["torque_top_lbft"] > t_limits["max_input_torque_lbft"]:
                continue
            # AI issue: It got confused betweenp payload weight and total weight. The correct check should be against the total weight (payload + chassis weight) against the max GCW limit.
            gross_combined_weight_actual = payload_weight + TRUCK_CHASSIS_REGISTRY[ch]["base_tractor_weight_lbs"]
            # Check if the gross combined weight exceeds the max GCWR limit of the chassis
            if gross_combined_weight_actual > TRUCK_CHASSIS_REGISTRY[ch]["max_chassis_gcwr_lbs"]:
                continue

            if gross_combined_weight_actual > t_limits["max_gcw_limit_lbs"]:
                continue
            # Eventually, want to add more checks for other constraints, such as axle load limits, bed payload weight, etc.
            
            validated_grid.append(
                {
                    "chassis_key": ch,
                    "engine_key": eng,
                    "transmission_key": trans,
                    "axle_ratio": axle,
                    "trailer_payload_lbs": payload_weight,
                    "weight_lbs": gross_combined_weight_actual,
                    "route": rt,
                }
            )

        print(
            f"Grid Processor: Ingested constraints and verified {len(validated_grid)} build combinations."
        )
        return validated_grid
