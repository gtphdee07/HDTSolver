# Module 1
import pandas as pd
import numpy as np
import itertools

# =====================================================================
# DATA REGISTRY ARCHITECTURE
# =====================================================================

TRANSMISSION_REGISTRY = {
    "Volvo_IShift_Direct": {
        "manufacturer": "Volvo",
        "model": "I-Shift AT Series",
        "type": "Direct Drive",
        "forward_gears": 12,
        "max_input_torque_lbft": 1920,
        "max_gcw_limit_lbs": 125000,
        "fluid_friction_loss_pct": 0.03,  # 3% power loss in top direct lockup gear
        "gears": {
            1: 14.94,
            2: 11.73,
            3: 9.04,
            4: 7.09,
            5: 5.54,
            6: 4.35,
            7: 3.44,
            8: 2.70,
            9: 2.08,
            10: 1.63,
            11: 1.28,
            12: 1.00,
        },
    },
    "Volvo_IShift_OD": {
        "manufacturer": "Volvo",
        "model": "I-Shift ATO Series",
        "type": "Overdrive",
        "forward_gears": 12,
        "max_input_torque_lbft": 1920,
        "max_gcw_limit_lbs": 125000,
        "fluid_friction_loss_pct": 0.06,  # 6% power loss in overdrive gear
        "gears": {
            1: 11.73,
            2: 9.21,
            3: 7.09,
            4: 5.57,
            5: 4.35,
            6: 3.41,
            7: 2.70,
            8: 2.12,
            9: 1.63,
            10: 1.28,
            11: 1.00,
            12: 0.78,
        },
    },
    "Eaton_Endurant_12": {
        "manufacturer": "Eaton Cummins",
        "model": "Endurant 12-Speed",
        "type": "Overdrive",
        "forward_gears": 12,
        "max_input_torque_lbft": 1850,
        "max_gcw_limit_lbs": 110000,
        "fluid_friction_loss_pct": 0.06,
        "gears": {
            1: 14.43,
            2: 11.05,
            3: 8.41,
            4: 6.43,
            5: 4.95,
            6: 3.79,
            7: 2.91,
            8: 2.23,
            9: 1.70,
            10: 1.30,
            11: 1.00,
            12: 0.77,
        },
    },
    # Add this entry to TRANSMISSION_REGISTRY
    "Ford_TorqShift_10R140": {
        "manufacturer": "Ford Motor Company",
        "model": "TorqShift 10R140",
        "type": "Overdrive",
        "forward_gears": 10,
        "max_input_torque_lbft": 1250,  # Built explicitly to handle Ford's extreme diesel profiles
        "max_gcw_limit_lbs": 43500,  # Maximum official Ford fifth-wheel/gooseneck combo safety limit
        "fluid_friction_loss_pct": 0.07,  # 7% fluid-friction parasitic penalty
        "gears": {
            1: 4.70,
            2: 2.99,
            3: 2.15,
            4: 1.80,
            5: 1.52,
            6: 1.28,
            7: 1.00,
            8: 0.85,
            9: 0.69,
            10: 0.64,
        },
    },
}

ENGINE_REGISTRY = {
    "Cummins_X15_Eff": {
        "manufacturer": "Cummins",
        "engine_family": "X15 Efficiency (450 ST2)",
        "displacement_liters": 14.9,
        "peak_hp": 450,
        "peak_hp_rpm": 1600,
        "torque_profile_type": "Multi-Torque",
        "torque_base_lbft": 1550,
        "torque_top_lbft": 1750,
        "flat_torque_start_rpm": 950,
        "flat_torque_end_rpm": 1300,
        "engine_redline_rpm": 1900,
        "max_braking_hp": 450,
        "engine_idle_rpm": 600,
        "engine_idle_torque_lbft": 700,
        "lugging_zone_risk": "High Damage Risk",
        "best_bsfc_value": 0.285,
        "bsfc_island_low_rpm": 1000,
        "bsfc_island_high_rpm": 1250,
        "bsfc_island_min_load_pct": 0.45,
        "bsfc_island_max_load_pct": 0.85,
        "outside_island_penalty_per_100rpm": 0.04,
    },
    "Cummins_X15_Perf": {
        "manufacturer": "Cummins",
        "engine_family": "X15 Performance (605)",
        "displacement_liters": 14.9,
        "peak_hp": 605,
        "peak_hp_rpm": 1700,
        "torque_profile_type": "Fixed Torque",
        "torque_base_lbft": 2050,
        "torque_top_lbft": 2050,
        "flat_torque_start_rpm": 1000,
        "flat_torque_end_rpm": 1400,
        "engine_redline_rpm": 2000,
        "max_braking_hp": 600,
        "engine_idle_rpm": 600,
        "engine_idle_torque_lbft": 800,
        "lugging_zone_risk": "High Damage Risk",
        "best_bsfc_value": 0.310,
        "bsfc_island_low_rpm": 1100,
        "bsfc_island_high_rpm": 1350,
        "bsfc_island_min_load_pct": 0.50,
        "bsfc_island_max_load_pct": 0.80,
        "outside_island_penalty_per_100rpm": 0.05,
    },
    "Volvo_D13TC": {
        "manufacturer": "Volvo",
        "engine_family": "D13 Turbo Compound (455TC)",
        "displacement_liters": 12.8,
        "peak_hp": 455,
        "peak_hp_rpm": 1400,
        "torque_profile_type": "Multi-Torque",
        "torque_base_lbft": 1750,
        "torque_top_lbft": 1850,
        "flat_torque_start_rpm": 900,
        "flat_torque_end_rpm": 1300,
        "engine_redline_rpm": 1900,
        "max_braking_hp": 530,
        "engine_idle_rpm": 600,
        "engine_idle_torque_lbft": 750,
        "lugging_zone_risk": "Low-Speed Adaptive",
        "best_bsfc_value": 0.278,
        "bsfc_island_low_rpm": 950,
        "bsfc_island_high_rpm": 1150,
        "bsfc_island_min_load_pct": 0.40,
        "bsfc_island_max_load_pct": 0.85,
        "outside_island_penalty_per_100rpm": 0.03,
    },
    # Add this entry to ENGINE_REGISTRY
'Ford_67L_Powerstroke_HO': {
    'manufacturer': 'Ford (Super Duty Powertrains)',
    'engine_family': '6.7L High Output Powerstroke V8',
    'displacement_liters': 6.7,
    'peak_hp': 500,
    'peak_hp_rpm': 2600,                # High speed light-truck diesel calibration profile
    'torque_profile_type': 'Fixed Torque Curve',
    'torque_base_lbft': 1200,
    'torque_top_lbft': 1200,
    'flat_torque_start_rpm': 1600,
    'flat_torque_end_rpm': 2200,
    'engine_redline_rpm': 4000,
    'max_braking_hp': 250,              # Traditional internal exhaust vane engine braking limit
    'engine_idle_rpm': 700,
    'engine_idle_torque_lbft': 450,
    'lugging_zone_risk': 'Severe Performance Drop',
    # BSFC Light-Duty Mapping Metrics
    'best_bsfc_value': 0.345,           # Small displacement high-rev diesel baseline
    'bsfc_island_low_rpm': 1500,
    'bsfc_island_high_rpm': 2100,
    'bsfc_island_min_load_pct': 0.35,
    'bsfc_island_max_load_pct': 0.80,
    'outside_island_penalty_per_100rpm': 0.06
}

}

TRUCK_CHASSIS_REGISTRY = {
    "Peterbilt_579_UltraLoft": {
        "manufacturer": "Peterbilt",
        "model": "579 UltraLoft",
        "base_tractor_weight_lbs": 18200,
        "drag_coefficient_cd": 0.46,
        "frontal_area_sqft": 104,
        "aero_constant_cda": 47.84,
        "max_chassis_gvw_lbs": 80000,
        "valid_engines": ["Cummins_X15_Eff", "Cummins_X15_Perf"],
        "valid_transmissions": ["Eaton_Endurant_12"],
        "valid_rear_end_ratios": [2.47, 2.64, 2.79, 2.93, 3.08, 3.25, 3.42],
    },
    "Volvo_VNL_860": {
        "manufacturer": "Volvo",
        "model": "VNL 860",
        "base_tractor_weight_lbs": 18900,
        "drag_coefficient_cd": 0.43,
        "frontal_area_sqft": 102,
        "aero_constant_cda": 43.86,
        "max_chassis_gvw_lbs": 80000,
        "valid_engines": ["Volvo_D13TC"],
        "valid_transmissions": ["Volvo_IShift_Direct", "Volvo_IShift_OD"],
        "valid_rear_end_ratios": [2.15, 2.28, 2.47, 2.64, 2.85, 2.93, 3.08],
    },
    "Kenworth_T680_NextGen": {
        "manufacturer": "Kenworth",
        "model": "T680 Next Gen",
        "base_tractor_weight_lbs": 18400,
        "drag_coefficient_cd": 0.45,
        "frontal_area_sqft": 103,
        "aero_constant_cda": 46.35,
        "max_chassis_gvw_lbs": 80000,
        "valid_engines": ["Cummins_X15_Eff", "Cummins_X15_Perf"],
        "valid_transmissions": ["Eaton_Endurant_12"],
        "valid_rear_end_ratios": [2.47, 2.64, 2.79, 2.93, 3.08, 3.25, 3.42],
    },
    # Add this entry to TRUCK_CHASSIS_REGISTRY
'Ford_F450_Pickup': {
    'manufacturer': 'Ford',
    'model': 'F-450 Super Duty (DRW Crew Cab)',
    'base_tractor_weight_lbs': 8600,     # Exceptionally lightweight compared to Class 8 frames
    'drag_coefficient_cd': 0.41,
    'frontal_area_sqft': 48,             # Considerably smaller frontal wind block area
    'aero_constant_cda': 19.68,          # 0.41 Cd * 48 SqFt
    'max_chassis_gvw_lbs': 14000,        # Standard pickup vehicle GVWR threshold
    # Relational verification block rules
    'valid_engines': ['Ford_67L_Powerstroke_HO'],
    'valid_transmissions': ['Ford_TorqShift_10R140'],
    'valid_rear_end_ratios': [4.30]      # Ford factory-standard production gear cut
}

}

ROUTE_SCENARIO_PROFILES = {
    "I95_Fuel_Slasher": {
        "description": "Flat long-haul corridor (East Coast flats)",
        "base_grade_pct": 0.0,
        "rolling_terrain_factor": 0.0,
        "speeds_to_test_mph": [55, 65, 75],
        "focus_metric": "Aerodynamic Fuel Optimization",
    },
    "I40_Midwest_Rhythm": {
        "description": "Rolling hills corridor (Midwest plains/highways)",
        "base_grade_pct": 0.0,
        "rolling_terrain_factor": 0.02,
        "speeds_to_test_mph": [55, 65, 75],
        "focus_metric": "Gear Hunting & Shift Frequency Index",
    },
    "I70_Mountain_Conqueror": {
        "description": "Severe mountain grades (Colorado Rockies / NC Blue Ridge)",
        "base_grade_pct": 6.0,
        "rolling_terrain_factor": 0.0,
        "speeds_to_test_mph": [35, 45, 55],
        "focus_metric": "Peak Gradeability & Downhill Braking Safety",
    },
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
