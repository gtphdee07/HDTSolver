# fleet_state.py - Shared Memory Repository for Multi-File Scoping
# This serves as the single source of truth across all modules.

TRANSMISSION_REGISTRY = {}
ENGINE_REGISTRY = {}
TRUCK_CHASSIS_REGISTRY = {}

ROUTE_SCENARIO_PROFILES = {
    'I95_Fuel_Slasher': {
        'description': 'Flat long-haul corridor', 'base_grade_pct': 0.0, 'rolling_terrain_factor': 0.0,
        'speeds_to_test_mph':[55,65,75], 'focus_metric': 'Aerodynamic Fuel Optimization'
    },
    'I40_Midwest_Rhythm': {
        'description': 'Rolling hills corridor', 'base_grade_pct': 0.0, 'rolling_terrain_factor': 0.02, 
        'speeds_to_test_mph':[55,65,75], 'focus_metric': 'Gear Hunting & Shift Frequency Index'
    },
    'I70_Mountain_Conqueror': {
        'description': 'Severe mountain grades', 'base_grade_pct': 6.0, 'rolling_terrain_factor': 0.0,
        'speeds_to_test_mph': [], # Handled dynamically by the dense mountain sweep loop
        'focus_metric': 'Peak Gradeability & Downhill Braking Safety'
    }
}
