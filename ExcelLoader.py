import pandas as pd
import numpy as np
import os
import fleet_state  # Imports the shared memory space module

class ExcelFleetDatabase:
    def __init__(self, excel_path="Fleet_Equipment_Database.xlsx"):
        self.excel_path = excel_path
        self.transmissions = {}
        self.engines = {}
        self.trucks = {}

    def load_database_from_excel(self):
        """
        Scans vertical sheets, reverses them into profiles, and natively
        publishes them straight into the global fleet_state memory scope.
        """
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(
                f"\n[Database Configuration Error]: Missing master file '{self.excel_path}'.\n"
                f"Please verify your ColumnarJSONToExcelConverter utility script has been executed!"
            )

        try:
            # 1. PARSE TRANSMISSIONS TAB
            df_t = pd.read_excel(self.excel_path, sheet_name='Transmissions')
            df_t = df_t.replace({np.nan: None})
            headers_t = list(df_t['Parameter_Header'])
            
            for col_name in df_t.columns:
                if col_name == 'Parameter_Header': continue
                col_data = list(df_t[col_name])
                t_key = col_data[headers_t.index("Transmission_Key")]
                
                self.transmissions[t_key] = {
                    "manufacturer": col_data[headers_t.index("Manufacturer")],
                    "model": col_data[headers_t.index("Model_Series")],
                    "type": col_data[headers_t.index("Drivetrain_Type")],
                    "forward_gears": int(col_data[headers_t.index("Forward_Gears_Count")]),
                    "max_input_torque_lbft": int(col_data[headers_t.index("Max_Input_Torque_lbft")]),
                    "max_gcw_limit_lbs": int(col_data[headers_t.index("Max_GCW_Limit_lbs")]),
                    "fluid_friction_loss_pct": float(col_data[headers_t.index("Fluid_Friction_Loss_Pct")]),
                    "gears": {}
                }
                for g in range(1, 13):
                    g_label = f"Gear_{g}_Ratio"
                    if g_label in headers_t:
                        val = col_data[headers_t.index(g_label)]
                        if val is not None and val != "":
                            self.transmissions[t_key]["gears"][int(g)] = float(val)

            # 2. PARSE ENGINES TAB
            df_e = pd.read_excel(self.excel_path, sheet_name='Engines')
            df_e = df_e.replace({np.nan: None})
            headers_e = list(df_e['Parameter_Header'])
            
            for col_name in df_e.columns:
                if col_name == 'Parameter_Header': continue
                col_data = list(df_e[col_name])
                e_key = col_data[headers_e.index("Engine_Key")]
                
                self.engines[e_key] = {}
                for h_idx, header_item in enumerate(headers_e):
                    if header_item == "Engine_Key": continue
                    val = col_data[h_idx]
                    clean_key = header_item.lower()
                    if val is not None:
                        if "rpm" in clean_key or "lbft" in clean_key or "hp" in clean_key:
                            self.engines[e_key][clean_key] = int(val)
                        elif "pct" in clean_key or "value" in clean_key or "penalty" in clean_key or "liters" in clean_key:
                            self.engines[e_key][clean_key] = float(val)
                        else:
                            self.engines[e_key][clean_key] = str(val)

            # 3. PARSE TRUCKS CHASSIS TAB
            df_ch = pd.read_excel(self.excel_path, sheet_name='Trucks_Chassis')
            df_ch = df_ch.replace({np.nan: None})
            headers_ch = list(df_ch['Parameter_Header'])
            
            for col_name in df_ch.columns:
                if col_name == 'Parameter_Header': continue
                col_data = list(df_ch[col_name])
                ch_key = col_data[headers_ch.index("Chassis_Key")]
                
                engines_list = [e.strip() for e in str(col_data[headers_ch.index("Valid_Engines_List")]).split(",")]
                trans_list = [t.strip() for t in str(col_data[headers_ch.index("Valid_Transmissions_List")]).split(",")]
                
                self.trucks[ch_key] = {
                    "manufacturer": col_data[headers_ch.index("Manufacturer")],
                    "model": col_data[headers_ch.index("Model_Designation")],
                    "base_tractor_weight_lbs": int(col_data[headers_ch.index("Base_Tractor_Weight_lbs")]),
                    "drag_coefficient_cd": float(col_data[headers_ch.index("Drag_Coefficient_Cd")]),
                    "frontal_area_sqft": int(col_data[headers_ch.index("Frontal_Area_SqFt")]),
                    "aero_constant_cda": float(col_data[headers_ch.index("Aero_Constant_CdA")]),
                    "max_chassis_gvwr_lbs": int(col_data[headers_ch.index("Max_Chassis_GVWR_lbs")]),
                    "max_chassis_gcwr_lbs": int(col_data[headers_ch.index("Max_Chassis_GCWR_lbs")]),
                    "valid_engines": engines_list,
                    "valid_transmissions": trans_list,
                    "valid_rear_end_ratios": []
                }
                for a in range(1, 11):
                    a_label = f"Rear_Axle_Ratio_{a}"
                    if a_label in headers_ch:
                        val = col_data[headers_ch.index(a_label)]
                        if val is not None and val != "":
                            self.trucks[ch_key]["valid_rear_end_ratios"].append(float(val))
                            
            # =================================================================
            # THE SINGLE SOURCE TRUTH BINDING: EXTEND TO SHARED MODULE SPACE
            # =================================================================
            fleet_state.TRANSMISSION_REGISTRY = self.transmissions
            fleet_state.ENGINE_REGISTRY = self.engines
            fleet_state.TRUCK_CHASSIS_REGISTRY = self.trucks
            
            print("Excel Engine: Master asset vectors loaded and broadcasted to shared state.")
        except Exception as e:
            raise ValueError(f"Excel Loading Failure: Row mismatch inside index unpacking loop. Details: {e}")

