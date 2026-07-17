# =====================================================================
# PIPELINE EXECUTION ENTRYPOINT
# =====================================================================
import MechanicalPhysicsCalculator
from RegistryDatabase import ROUTE_SCENARIO_PROFILES
import ScenarioExecutionWrapper
import FleetDataVisualizer
from ExcelLoader import ExcelFleetDatabase

#from RegistryDatabase import TRUCK_CHASSIS_REGISTRY, ENGINE_REGISTRY, TRANSMISSION_REGISTRY


# =====================================================================
# SYSTEM AUTOMATION PIPELINE INITIALIZATION EXECUTION
# =====================================================================
if __name__ == '__main__':
    # 1. Instantiate the column-oriented Excel parser object
    # This reads Fleet_Equipment_Database.xlsx and populates the global dictionaries!
    fleet_db = ExcelFleetDatabase(excel_path="Fleet_Equipment_Database.xlsx")
    fleet_db.load_database_from_excel()

    # 2. Re-assign the master data boundaries so Module 3 reads your Excel parameters natively
    TRANSMISSION_REGISTRY = fleet_db.transmissions
    ENGINE_REGISTRY = fleet_db.engines
    TRUCK_CHASSIS_REGISTRY = fleet_db.trucks
    #ROUTE_SCENARIO_PROFILES = fleet_db.

    # 3. Initialize the core physics calculator and Module 3
    physics_calc = MechanicalPhysicsCalculator.MechanicalPhysicsCalculator()
    wrapper_engine = ScenarioExecutionWrapper.ScenarioExecutionWrapper(physics_calc)

    # 4. Define the user research criteria query
    user_request = {
        'chassis': ['Volvo_VNL_860', 'Kenworth_T680_NextGen', 'Ford_F450_Pickup'],
        'engine': ['ALL_VALID'], 
        'transmission': ['ALL_VALID'], 
        'axle_ratio': ['ALL_VALID'],
        'trailer_payload_lbs':[23500], 
        'route_corridor': ['I95_Fuel_Slasher', 'I40_Midwest_Rhythm', 'I70_Mountain_Conqueror']
    }

    print("--- PIPELINE CORE TRIGGERED: SWEEPING EXCEL CONFIGURATIONS ---")
    # This call passes your request to Module 3, which executes your Excel specs seamlessly!
    tidy_df = wrapper_engine.execute_scenario_sweep(
        user_request, 
        ['I95_Fuel_Slasher', 'I40_Midwest_Rhythm', 'I70_Mountain_Conqueror']
    )

    # 5. Compile Excel tabs and render the 8 high-resolution presentation charts
    wrapper_engine.export_to_multi_tab_excel(tidy_df, "Fleet_Executive_Decision_Matrix.xlsx")
    visualizer = FleetDataVisualizer.FleetDataVisualizer(output_dir="executive_presentation_charts", palette="Set1")
    visualizer.generate_executive_visual_report(tidy_df)


    







