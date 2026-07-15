# Module 1
import pandas as pd
import numpy as np
import itertools
import json
import os

# =====================================================================
# DYNAMIC EXTERNAL REGISTRY DATABASE LOADER
# =====================================================================

class RegistryDatabase:
    def __init__(self, registry_dir="registries"):
        """Initializes pointers for the three core relational registries."""
        self.directory = registry_dir
        self.transmissions = {}
        self.engines = {}
        self.trucks = {}

    def load_database(self):
        """
        Natively reads external JSON files and performs an immediate
        integrity audit to prevent typographical and structural errors.
        """
        try:
            # Resolve absolute path locations based on your directory setting
            trans_path = os.path.join(self.directory, "transmissions.json")
            engine_path = os.path.join(self.directory, "engines.json")
            trucks_path = os.path.join(self.directory, "trucks.json")

            # Execute clean stream loading loops
            with open(trans_path, "r") as f:
                # Converts string-based gear keys ("1", "2") to integers for math engine compatibility
                raw_trans = json.load(f)
                self.transmissions = {
                    k: {**v, 'gears': {int(g_k): g_v for g_k, g_v in v['gears'].items()}}
                    for k, v in raw_trans.items()
                }

            with open(engine_path, "r") as f:
                self.engines = json.load(f)

            with open(trucks_path, "r") as f:
                self.trucks = json.load(f)

            # Fire the automated database safety gatekeeper
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
                f"\n[JSON Syntax Error]: A text file contains an illegal format character "
                f"(missing quote, unclosed brace, or a misplaced comma).\nDetails: {e}"
            )

    def _audit_structural_integrity(self):
        """
        The Gatekeeper. Automatically scans the expanded data fields to ensure
        mandatory variables exist and cross-referenced keys match across records.
        """
        mandatory_truck_fields = ['base_tractor_weight_lbs', 'aero_constant_cda', 'valid_engines', 'valid_transmissions']
        
        for truck_key, specs in self.trucks.items():
            # 1. Enforce schema compliance
            for field in mandatory_truck_fields:
                if field not in specs:
                    raise KeyError(f"Registry Validation Failure: '{truck_key}' is missing the mandatory '{field}' field!")
            
            # 2. Audit cross-references (catches spelling differences between files)
            for eng_key in specs['valid_engines']:
                if eng_key not in self.engines:
                    raise ValueError(f"Integrity Link Error: Truck '{truck_key}' references engine '{eng_key}', but that key is missing inside engines.json!")
                    
            for trans_key in specs['valid_transmissions']:
                if trans_key not in self.transmissions:
                    raise ValueError(f"Integrity Link Error: Truck '{truck_key}' references transmission '{trans_key}', but that key is missing inside transmissions.json!")


# --- INSTANTIATE AND FILL GLOBAL Pointers FOR THE ENTIRE PIPELINE ---
db_loader = RegistryDatabase(registry_dir="registries")
db_loader.load_database()

# These variables now point to the validated JSON contents, keeping Module 1, 2, and 3 completely unbroken
TRANSMISSION_REGISTRY = db_loader.transmissions
ENGINE_REGISTRY = db_loader.engines
TRUCK_CHASSIS_REGISTRY = db_loader.trucks

# =====================================================================
# SYSTEM MISSION SCENARIOS (REMAINS INTEGRATED)
# =====================================================================
ROUTE_SCENARIO_PROFILES = {
    'I95_Fuel_Slasher': {
        'description': 'Flat long-haul corridor (East Coast flats)',
        'base_grade_pct': 0.0, 'rolling_terrain_factor': 0.0,
        'speeds_to_test_mph':, 'focus_metric': 'Aerodynamic Fuel Optimization'
    },
    'I40_Midwest_Rhythm': {
        'description': 'Rolling hills corridor (Midwest plains/highways)',
        'base_grade_pct': 0.0, 'rolling_terrain_factor': 0.02, 
        'speeds_to_test_mph':, 'focus_metric': 'Gear Hunting & Shift Frequency Index'
    },
    'I70_Mountain_Conqueror': {
        'description': 'Severe mountain grades (Colorado Rockies / NC Blue Ridge)',
        'base_grade_pct': 6.0, 'rolling_terrain_factor': 0.0,
        'speeds_to_test_mph':, 'focus_metric': 'Peak Gradeability & Downhill Braking Safety'
    }
}


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

            weights = user_input["total_weight_lbs"]
            routes = user_input["route_corridor"]

            chassis_grid = list(
                itertools.product(
                    [ch_key], engines, transmissions, axles, weights, routes
                )
            )
            raw_permutations.extend(chassis_grid)

        validated_grid = []
        for row in raw_permutations:
            ch, eng, trans, axle, w, rt = row
            t_limits = TRANSMISSION_REGISTRY[trans]
            e_limits = ENGINE_REGISTRY[eng]

            if e_limits["torque_top_lbft"] > t_limits["max_input_torque_lbft"]:
                continue
            if w > t_limits["max_gcw_limit_lbs"]:
                continue

            validated_grid.append(
                {
                    "chassis_key": ch,
                    "engine_key": eng,
                    "transmission_key": trans,
                    "axle_ratio": axle,
                    "weight_lbs": w,
                    "route": rt,
                }
            )

        print(
            f"Grid Processor: Ingested constraints and verified {len(validated_grid)} build combinations."
        )
        return validated_grid
