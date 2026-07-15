# =====================================================================
# PIPELINE EXECUTION ENTRYPOINT
# =====================================================================
import MechanicalPhysicsCalculator
import ScenarioExecutionWrapper
import FleetDataVisualizer
#from RegistryDatabase import TRUCK_CHASSIS_REGISTRY, ENGINE_REGISTRY, TRANSMISSION_REGISTRY


if __name__ == '__main__':
    # 1. Initialize Core Engine Objects
    physics_calc = MechanicalPhysicsCalculator.MechanicalPhysicsCalculator()
    wrapper_engine = ScenarioExecutionWrapper.ScenarioExecutionWrapper(physics_calc)

    # 2. Define User Testing Sweep Parameters
    # We pass lists for variables to test multiple combinations at once.
    # We use route scenario keys to match real-world speeds automatically.
    user_request = {
        'chassis': ['Volvo_VNL_860', 'Kenworth_T680_NextGen','Ford_F450_Pickup'],
        'engine': ['ALL_VALID'],          # Expands to approved engines for that chassis
        'transmission': ['ALL_VALID'],    # Expands to approved transmissions
        'axle_ratio': [2.47, 2.64, 3.08, 4.10, 4.30], # Rear end options to compare side-by-side
        'payload_weight_lbs':[23500], # Light vs heavy trailer configuration test
        'route_corridor': ['I95_Fuel_Slasher', 'I70_Mountain_Conqueror','I40_Midwest_Rhythm']
        #'route_corridor': ['I40_Midwest_Rhythm']
    }

    # Updated example inside your execution block to run a multi-truck sweep:
    # user_request = {
    #     'chassis': ['Volvo_VNL_860', 'Kenworth_T680_NextGen', 'Ford_F450_Pickup'], # Ford added cleanly!
    #     'engine': ['ALL_VALID'],
    #     'transmission': ['ALL_VALID'],
    #     'axle_ratio': ['ALL_VALID'], # Resolves to 4.30 automatically for the Ford, and fleet gears for semis
    #     'payload_weight_lbs':, # Simulates your current real-world trailer weight
    #     'route_corridor': ['I95_Fuel_Slasher', 'I70_Mountain_Conqueror']
    # }








    # 3. Execute and capture the Tidy (Long-Form) DataFrame
    print("--- STARTING COGNITIVE FLEET RUN SWEEP ---")
    tidy_df = wrapper_engine.execute_scenario_sweep(user_request, ['I95_Fuel_Slasher', 'I70_Mountain_Conqueror', 'I40_Midwest_Rhythm'])

    # 4. Display clean table sample out to screen terminal for instant check
    print("\n--- SAMPLE OUTPUT: TIDY DATAFRAME FOR GRAPHING ENGINES ---")
    print(tidy_df[['Truck_Model', 'Engine_Series', 'Axle_Ratio', 'Route_Scenario', 'Speed_MPH', 'Calculated_MPG']].head(12))

    # 5. Reshape and push straight out to an enterprise multi-tab Excel spreadsheet workbook
    wrapper_engine.export_to_multi_tab_excel(tidy_df, "Fleet_Executive_Decision_Matrix.xlsx")

      # 1. Run your core physics simulation loops to fetch the master dataset
    # tidy_df = wrapper_engine.execute_scenario_sweep(user_request, ...)
    
    # 2. Instantiate the isolated graphics module
    visualizer = FleetDataVisualizer.FleetDataVisualizer(output_dir="executive_presentation_charts", palette="Set1")
    
    # 3. Call the supervisor wrapper to generate exactly what you need
    report_manifest = visualizer.generate_executive_visual_report(tidy_df, active_graph_ids=[8])

    







