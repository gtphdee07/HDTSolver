import pandas as pd
import json
import os

class ColumnarJSONToExcelConverter:
    def __init__(self, source_dir="registries", output_file="Fleet_Equipment_Database.xlsx"):
        self.source_dir = source_dir
        self.output_file = output_file

    def convert_all(self):
        print("Converter Engine: Re-architecting database into vertical columns...")
        
        # =====================================================================
        # 1. TRANSLATE TRANSMISSIONS
        # =====================================================================
        with open(os.path.join(self.source_dir, "transmissions.json"), "r") as f:
            raw_trans = json.load(f)
            
        trans_dict = {
            "Parameter_Header": [
                "Transmission_Key", "Manufacturer", "Model_Series", "Drivetrain_Type", 
                "Forward_Gears_Count", "Max_Input_Torque_lbft", "Max_GCW_Limit_lbs", "Fluid_Friction_Loss_Pct"
            ] + [f"Gear_{g}_Ratio" for g in range(1, 13)]
        }
        
        for key, v in raw_trans.items():
            base_specs = [
                key, v["manufacturer"], v["model"], v["type"], 
                v["forward_gears"], v["max_input_torque_lbft"], v["max_gcw_limit_lbs"], v["fluid_friction_loss_pct"]
            ]
            gear_specs = [v["gears"].get(str(g), "") for g in range(1, 13)]
            trans_dict[key] = base_specs + gear_specs
            
        df_trans = pd.DataFrame(trans_dict)

        # =====================================================================
        # 2. TRANSLATE ENGINES
        # =====================================================================
        with open(os.path.join(self.source_dir, "engines.json"), "r") as f:
            raw_engines = json.load(f)
            
        first_engine_key = list(raw_engines.keys())[0]
        engine_fields = list(raw_engines[first_engine_key].keys())
        
        engine_dict = {
            "Parameter_Header": ["Engine_Key"] + [field.upper() for field in engine_fields]
        }
        
        for key, v in raw_engines.items():
            specs = [key] + [v[field] for field in engine_fields]
            engine_dict[key] = specs
            
        df_engines = pd.DataFrame(engine_dict)

        # =====================================================================
        # 3. TRANSLATE TRUCKS (ALIGNED TO YOUR EXACT NEW GVWR/GCWR KEYS)
        # =====================================================================
        with open(os.path.join(self.source_dir, "trucks.json"), "r") as f:
            raw_trucks = json.load(f)
            
        truck_dict = {
            "Parameter_Header": [
                "Chassis_Key", "Manufacturer", "Model_Designation", "Base_Tractor_Weight_lbs", 
                "Drag_Coefficient_Cd", "Frontal_Area_SqFt", "Aero_Constant_CdA", 
                "Max_Chassis_GVWR_lbs", "Max_Chassis_GCWR_lbs", # Stamped to match your file keys natively!
                "Valid_Engines_List", "Valid_Transmissions_List"
            ] + [f"Rear_Axle_Ratio_{a}" for a in range(1, 11)]
        }
        
        for key, v in raw_trucks.items():
            # Graceful fallbacks using .get() to catch potential key mismatches across assets
            gvwr = v.get("max_chassis_gvwr_lbs", v.get("max_chassis_gvw_lbs", 80000))
            gcwr = v.get("max_chassis_gcwr_lbs", v.get("max_chassis_gvw_lbs", 80000))
            axles = v.get("valid_rear_end_ratios", [])
            
            axle_slots = [axles[i] if i < len(axles) else "" for i in range(10)]
            
            base_specs = [
                key, v["manufacturer"], v["model"], v["base_tractor_weight_lbs"], 
                v["drag_coefficient_cd"], v["frontal_area_sqft"], v["aero_constant_cda"], 
                gvwr, gcwr,
                ", ".join(v["valid_engines"]), ", ".join(v["valid_transmissions"])
            ]
            truck_dict[key] = base_specs + axle_slots
            
        df_trucks = pd.DataFrame(truck_dict)

        # =====================================================================
        # 4. EXPORT WORKBOOK
        # =====================================================================
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            df_trucks.to_excel(writer, sheet_name='Trucks_Chassis', index=False)
            df_engines.to_excel(writer, sheet_name='Engines', index=False)
            df_trans.to_excel(writer, sheet_name='Transmissions', index=False)

        print(f"Success: Columnar template synced and compiled to -> '{self.output_file}'")

if __name__ == "__main__":
    converter = ColumnarJSONToExcelConverter()
    converter.convert_all()
