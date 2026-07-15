import pandas as pd
import json
import os

# Ensure your local machine has openpyxl: pip install pandas openpyxl

class JSONToExcelConverter:
    def __init__(self, source_dir="registries", output_file="Fleet_Equipment_Database.xlsx"):
        self.source_dir = source_dir
        self.output_file = output_file

    def convert_all(self):
        print("Converter Engine: Initializing JSON to Excel database migration...")
        
        # 1. Ingest Transmissions
        with open(os.path.join(self.source_dir, "transmissions.json"), "r") as f:
            raw_trans = json.load(f)
        
        trans_rows = []
        for key, v in raw_trans.items():
            row = {
                "Transmission_ID": key,
                "Manufacturer": v["manufacturer"],
                "Model": v["model"],
                "Type": v["type"],
                "Forward_Gears": v["forward_gears"],
                "Max_Input_Torque_lbft": v["max_input_torque_lbft"],
                "Max_GCW_Limit_lbs": v["max_gcw_limit_lbs"],
                "Fluid_Friction_Loss_Pct": v["fluid_friction_loss_pct"]
            }
            # Flatten up to 12 gears dynamically across columns
            for g in range(1, 13):
                row[f"Gear_{g}_Ratio"] = v["gears"].get(str(g), None)
            trans_rows.append(row)
        df_trans = pd.DataFrame(trans_rows)
        df_trans_transposed = df_trans.transpose()

        # 2. Ingest Engines
        with open(os.path.join(self.source_dir, "engines.json"), "r") as f:
            raw_engines = json.load(f)
        
        engine_rows = []
        for key, v in raw_engines.items():
            row = {"Engine_ID": key}
            # Safely capture all flat dictionary fields from the json mapping layout
            for k, val in v.items():
                row[k.title()] = val
            engine_rows.append(row)
        df_engines = pd.DataFrame(engine_rows)
        df_engines_transposed = df_engines.transpose()

        # 3. Ingest Trucks
        with open(os.path.join(self.source_dir, "trucks.json"), "r") as f:
            raw_trucks = json.load(f)
        
        truck_rows = []
        for key, v in raw_trucks.items():
            row = {
                "Chassis_ID": key,
                "Manufacturer": v["manufacturer"],
                "Model": v["model"],
                "Base_Tractor_Weight_lbs": v["base_tractor_weight_lbs"],
                "Drag_Coefficient_Cd": v["drag_coefficient_cd"],
                "Frontal_Area_SqFt": v["frontal_area_sqft"],
                "Aero_Constant_CdA": v["aero_constant_cda"],
                "Max_Chassis_GVWR_lbs": v["max_chassis_gvwr_lbs"],
                "Valid_Engines": ", ".join(v["valid_engines"]),
                "Valid_Transmissions": ", ".join(v["valid_transmissions"]),
                "Valid_Rear_End_Ratios": ", ".join(map(str, v["valid_rear_end_ratios"]))
            }
            truck_rows.append(row)
        df_trucks = pd.DataFrame(truck_rows)

        # 4. Save to Multi-Tab Master Excel Sheet
        df_trucks_transposed = df_trucks.transpose()
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            df_trucks_transposed.to_excel(writer, sheet_name='Trucks_Chassis', index=False)
            df_engines_transposed.to_excel(writer, sheet_name='Engines', index=False)
            df_trans_transposed.to_excel(writer, sheet_name='Transmissions', index=False)

        print(f"Success: Migrated registries into master database workbook: '{self.output_file}'")

if __name__ == "__main__":
    converter = JSONToExcelConverter()
    converter.convert_all()

