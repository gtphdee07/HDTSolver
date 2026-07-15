import pandas as pd
import numpy as np
import os

# =====================================================================
# INDEPENDENT COMMERCIAL O&M FINANCIAL LIFE-CYCLE ENGINE
# =====================================================================

class FleetFinanceEngine:
    def __init__(self, database_path="Fleet_Equipment_Database.xlsx"):
        self.database_path = database_path
        self.financial_profiles = {}
        
        # --- CLASS-STANDARD REPAIR INTERVALS AND COST RECOVERY FALLBACKS ---
        # Safeguards execution: safely applied if custom rows are omitted from the sheet
        self.CLASS_8_DEFAULT_OM = {
            "pm_interval_miles": 45000, "pm_cost_est": 750,
            "valve_overhead_interval_miles": 150000, "valve_overhead_cost": 1500,
            "dpf_clean_interval_miles": 250000, "dpf_clean_cost": 3500,
            "amt_clutch_interval_miles": 550000, "amt_clutch_cost": 6500,
            "major_overhaul_interval_miles": 800000, "major_overhaul_cost": 26000
        }
        
        self.CLASS_4_DEFAULT_OM = {
            "pm_interval_miles": 10000, "pm_cost_est": 280,
            "valve_overhead_interval_miles": 999999, "valve_overhead_cost": 0, # N/A for standard pickup blocks
            "dpf_clean_interval_miles": 150000, "dpf_clean_cost": 2400,
            "amt_clutch_interval_miles": 220000, "amt_clutch_cost": 5500, # Maps automatic transmission overhauls
            "major_overhaul_interval_miles": 320000, "major_overhaul_cost": 16000 # Full engine swap replacement
        }

    def load_lifecycle_registry(self):
        """
        Dynamically scans for an optional '[O&M_Lifecycle_Specs]' tab inside the master Excel workbook.
        If missing, it notes the absence and relies gracefully on internal class fallbacks.
        """
        if not os.path.exists(self.database_path):
            print(f"[Finance System]: Note: '{self.database_path}' not found yet. Defaulting entirely to Class-Standard logic matrices.")
            return

        try:
            # Read financial tab from master workbook
            df_fin = pd.read_excel(self.database_path, sheet_name='O&M_Lifecycle_Specs')
            for _, row in df_fin.iterrows():
                key = row['Engine_Transmission_Link']
                self.financial_profiles[key] = {
                    "pm_interval_miles": int(row['PM_Interval_Miles']),
                    "pm_cost_est": float(row['PM_Cost_Est']),
                    "valve_overhead_interval_miles": int(row['Valve_Overhead_Interval_Miles']),
                    "valve_overhead_cost": float(row['Valve_Overhead_Cost']),
                    "dpf_clean_interval_miles": int(row['DPF_Clean_Interval_Miles']),
                    "dpf_clean_cost": float(row['DPF_Clean_Cost']),
                    "amt_clutch_interval_miles": int(row['AMT_Clutch_Interval_Miles']),
                    "amt_clutch_cost": float(row['AMT_Clutch_Cost']),
                    "major_overhaul_interval_miles": int(row['Major_Overhaul_Interval_Miles']),
                    "major_overhaul_cost": float(row['Major_Overhaul_Cost'])
                }
            print("Finance System: Custom lifecycle spec sheet parsed successfully.")
        except Exception:
            print("[Finance System Notification]: 'O&M_Lifecycle_Specs' tab omitted from Excel. Using automated fallback variables.")

    def generate_5year_spending_plan(self, engine_key, unit_profile):
        """
        Ingests specific used vehicle telemetry metadata, runs engine-hour 
        reality index checks, and builds out year-by-year maintenance cost timelines.
        """
        # 1. Resolve Class-Standard Fallback Assignment Profiles
        if engine_key in self.financial_profiles:
            om_spec = self.financial_profiles[engine_key]
        else:
            om_spec = self.CLASS_4_DEFAULT_OM if 'Ford' in engine_key else self.CLASS_8_DEFAULT_OM
            print(f"[Dynamic Assignment]: Mapping baseline class defaults for candidate engine '{engine_key}'.")

        # 2. Engine Hour Idling Reality Check Matrix Formula
        odometer_miles = unit_profile['current_odometer_miles']
        hours_wear_proxy = unit_profile['total_engine_hours'] * 30
        
        # Base engine wear locks to whichever index calculation is higher
        starting_wear_miles = max(odometer_miles, hours_wear_proxy)
        if hours_wear_proxy > odometer_miles:
            print(f"[Warning Warning]: Excessive vehicle idling hours detected! True internal engine wear calibrated to "
                  f"{hours_wear_proxy:,} miles vs odometer reading of {odometer_miles:,} miles.")

        annual_utilization = unit_profile['anticipated_rv_miles_per_year']
        current_cumulative_miles = starting_wear_miles
        
        yearly_projection_logs = []

        # 3. Chronological 5-Year Financial Lifecycle Simulation Loop
        for year in range(1, 6):
            year_start_miles = current_cumulative_miles
            year_end_miles = current_cumulative_miles + annual_utilization
            
            annual_pm_cost = 0
            annual_repair_cost = 0
            bill_items = []

            # Loop mileage increments step-by-step through the current year's timeline
            for mile in range(year_start_miles + 1, year_end_miles + 1):
                
                # Check A: Routine Fluid Service Intervals
                if mile % om_spec['pm_interval_miles'] == 0:
                    annual_pm_cost += om_spec['pm_cost_est']
                    if "Routine PM Service" not in bill_items: bill_items.append("Routine PM Service")
                
                # Check B: Top-End Overhead Valve / Tuning Checks
                if mile % om_spec['valve_overhead_interval_miles'] == 0:
                    annual_repair_cost += om_spec['valve_overhead_cost']
                    bill_items.append("Valve Overhead Calibration")
                    
                # Check C: DPF Ash Baking Core De-scaling
                if mile % om_spec['dpf_clean_interval_miles'] == 0:
                    annual_repair_cost += om_spec['dpf_clean_cost']
                    bill_items.append("DPF Emissions Baking")
                    
                # Check D: Transmission Heavy Clutch / Hydraulic Actuator Overhauls
                if mile % om_spec['amt_clutch_interval_miles'] == 0:
                    annual_repair_cost += om_spec['amt_clutch_cost']
                    bill_items.append("Transmission Clutch/Actuator Overhaul")
                    
                # Check E: Complete Structural In-Frame Remanufacturing Milestone Block
                if mile % om_spec['major_overhaul_interval_miles'] == 0:
                    annual_repair_cost += om_spec['major_overhaul_cost']
                    bill_items.append("CRITICAL: Major Engine In-Frame Overhaul")

            # Low utilization calendar guard rule: enforce at least 1 fluid check per year
            if annual_pm_cost == 0:
                annual_pm_cost = om_spec['pm_cost_est']
                bill_items.append("Annual Time-Based Fluid Service")

            total_year_spend = annual_pm_cost + annual_repair_cost
            
            yearly_projection_logs.append({
                'Year': f"Year {year}",
                'Start_Odo_Miles': int(year_start_miles),
                'End_Odo_Miles': int(year_end_miles),
                'Routine_PM_Cost': round(annual_pm_cost, 2),
                'Major_Repair_Cost': round(annual_repair_cost, 2),
                'Total_Annual_Spend': round(total_year_spend, 2),
                'Triggered_Repairs_List': ", ".join(bill_items) if bill_items else "Routine Maintenance Only"
            })
            
            # Advance odometer baseline for the next simulated year block
            current_cumulative_miles = year_end_miles

        return pd.DataFrame(yearly_projection_logs)

    def plot_5year_cash_burn_old(self, spending_df, output_dir="financial_reports", file_name="graph_11_cash_burn.png"):
        """
        Generates the 5-Year Cumulative Operating Expenditure Curve.
        Visualizes the progression of routine PM costs stacked beneath major repair spikes.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Ensure target reporting path exists on disk
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 1. Financial Data Transformation Lines
        # Calculate continuous cumulative sums over the 5-year timeline
        spending_df['Cum_PM_Cost'] = spending_df['Routine_PM_Cost'].cumsum()
        spending_df['Cum_Total_Cost'] = spending_df['Total_Annual_Spend'].cumsum()

        # Set up a clean, professional financial grid template style
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(11, 6))

        # 2. Render Stacked Cash Regions
        # Draw the total cost line as the outer bound, filling the area beneath it
        ax.plot(spending_df['Year'], spending_df['Cum_Total_Cost'], color='darkred', marker='o', linewidth=3, label='Total Accumulated Cash Outlay')
        ax.fill_between(spending_df['Year'], spending_df['Cum_Total_Cost'], color='darkred', alpha=0.15)

        # Overlay the baseline routine maintenance fluid cost region
        ax.plot(spending_df['Year'], spending_df['Cum_PM_Cost'], color='darkblue', marker='s', linewidth=2, linestyle=':', label='Routine Maintenance (Fluids/Lube Only)')
        ax.fill_between(spending_df['Year'], spending_df['Cum_PM_Cost'], color='darkblue', alpha=0.1)

        # 3. Dynamic Visual Annotation Layer (Highlights specific component triggers)
        for idx, row in spending_df.iterrows():
            total_spend = row['Cum_Total_Cost']
            triggers = row['Triggered_Repairs_List']
            
            # If the year contains a major high-dollar repair, stamp an explicit flag on the graph
            if "Overhaul" in triggers or "Clutch" in triggers or "Emissions" in triggers:
                # Truncate text string slightly so it fits inside the visual grid bounds neatly
                clean_trigger_text = triggers.replace("CRITICAL: ", "").split(",")[0]
                
                ax.annotate(
                    f"⚠️ {clean_trigger_text}\nTotal Outlay: ${int(total_spend):,}",
                    xy=(row['Year'], total_spend),
                    xytext=(0, 20), textcoords='offset points',
                    arrowprops=dict(arrowstyle="->", color='black', lw=1),
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.6, ec="black"),
                    ha='center', fontsize=9, fontweight='semibold'
                )

        # 4. Formatter and Label Specifications
        ax.set_title('Graph 11: Used Tractor 5-Year Cumulative Operating Expenditure Curve\n(Operations & Maintenance Forward Spending Timeline)', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Years of Active RV Ownership', fontsize=12, labelpad=10)
        ax.set_ylabel('Total Accumulated Expenses ($)', fontsize=12, labelpad=10)
        
        # Reformat the Y-Axis tick markers into crisp financial currency labels
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        
        ax.legend(loc='upper left', frameon=True, shadow=False)
        plt.tight_layout()

        # Save high-resolution asset to disk
        save_path = os.path.join(output_dir, file_name)
        plt.savefig(save_path, dpi=300)
        plt.close()
        
        print(f"\nFinancial Graphics Engine: Successfully compiled expenditure curve graph to '{save_path}'")
        return save_path
    def plot_5year_cash_burn(self, engine_key, unit_profile, spending_df, output_dir="financial_reports"):
        """
        Generates the 5-Year Cumulative Operating Expenditure Curve.
        Natively stamps input profile criteria onto the visual canvas and 
        exports a uniquely parameterized file asset name for easy comparisons.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Ensure target reporting path exists on disk
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 1. DYNAMIC FILE NAME GENERATION PIPELINE
        # Sanitizes keys and constructs a completely unique descriptor string
        chassis_clean = engine_key.lower().replace(" ", "_")
        age = unit_profile['truck_age_years']
        miles = unit_profile['current_odometer_miles']
        mpy = unit_profile['anticipated_rv_miles_per_year']
        
        unique_file_name = f"cashburn_{chassis_clean}_{age}yr_{miles}mi_{mpy}mpy.png"
        save_path = os.path.join(output_dir, unique_file_name)

        # 2. Financial Data Transformation Lines
        spending_df['Cum_PM_Cost'] = spending_df['Routine_PM_Cost'].cumsum()
        spending_df['Cum_Total_Cost'] = spending_df['Total_Annual_Spend'].cumsum()

        # Set up financial template grid style
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(12, 6.5))

        # 3. Render Stacked Cash Regions
        ax.plot(spending_df['Year'], spending_df['Cum_Total_Cost'], color='darkred', marker='o', linewidth=3, label='Total Accumulated Cash Outlay')
        ax.fill_between(spending_df['Year'], spending_df['Cum_Total_Cost'], color='darkred', alpha=0.15)

        ax.plot(spending_df['Year'], spending_df['Cum_PM_Cost'], color='darkblue', marker='s', linewidth=2, linestyle=':', label='Routine Maintenance (Fluids/Lube Only)')
        ax.fill_between(spending_df['Year'], spending_df['Cum_PM_Cost'], color='darkblue', alpha=0.1)

        # 4. METADATA STAMPING LAYER (The Blueprint Box)
        # Renders all input criteria cleanly on the graph so the user instantly knows which truck this is
        metadata_text = (
            f"=== LISTING BLUEPRINT ===\n"
            f"Engine Target: {engine_key.replace('_', ' ')}\n"
            f"Asset Age: {age} Years Old\n"
            f"Odometer Reading: {miles:,} Miles\n"
            f"Engine Hours: {unit_profile['total_engine_hours']:,} Hours\n"
            f"Projected RV Usage: {mpy:,} Miles / Year"
        )
        
        # Places the data box securely in the top-center zone of the chart canvas
        ax.text(
            0.5, 0.95, metadata_text,
            transform=ax.transAxes, fontsize=10, fontweight='semibold',
            fontfamily='monospace', color='black',
            bbox=dict(boxstyle="square,pad=0.6", fc="white", alpha=0.9, ec="gray", lw=1),
            ha='center', va='top'
        )

        # 5. Dynamic Repair Annotation Flags
        for idx, row in spending_df.iterrows():
            total_spend = row['Cum_Total_Cost']
            triggers = row['Triggered_Repairs_List']
            
            if "Overhaul" in triggers or "Clutch" in triggers or "Emissions" in triggers:
                clean_trigger_text = triggers.replace("CRITICAL: ", "").split(",")
                # Grab just the first major repair flag text to avoid chart overlap clutter
                display_text = clean_trigger_text[0].strip()
                if len(clean_trigger_text) > 1: display_text += "..."
                
                ax.annotate(
                    f"⚠️ {display_text}\nOutlay: ${int(total_spend):,}",
                    xy=(row['Year'], total_spend),
                    xytext=(0, 22), textcoords='offset points',
                    arrowprops=dict(arrowstyle="->", color='black', lw=1),
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.7, ec="black"),
                    ha='center', fontsize=8.5, fontweight='semibold'
                )

        # 6. Formatter and Axis Specifications
        ax.set_title('Graph 11: Used Tractor 5-Year Cumulative Operating Expenditure Curve\n(Operations & Maintenance Forward Spending Timeline)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Years of Active RV Ownership', fontsize=12, labelpad=12)
        ax.set_ylabel('Total Accumulated Expenses ($)', fontsize=12, labelpad=12)
        
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        ax.set_ylim(0, max(spending_df['Cum_Total_Cost'].max() * 1.25, 10000)) # Pads top margin cleanly
        
        ax.legend(loc='upper left', frameon=True, shadow=False)
        plt.tight_layout()

        # Save high-resolution unique asset to disk
        plt.savefig(save_path, dpi=300)
        plt.close()
        
        print(f"\nFinancial Graphics Engine: Successfully compiled unique report asset to -> '{save_path}'")
        return save_path


# =====================================================================
# INDEPENDENT TEST BENCH TRIGGERS
# =====================================================================
# =====================================================================
# INDEPENDENT TEST BENCH TRIGGERS
# =====================================================================
# =====================================================================
# INDEPENDENT TEST BENCH TRIGGERS
# =====================================================================
if __name__ == '__main__':
    # Initialize the independent finance tracker class module object
    finance_engine = FleetFinanceEngine(database_path="Fleet_Equipment_Database.xlsx")
    finance_engine.load_lifecycle_registry()

    # Define a real used listing profile example
    used_volvo_listing = {
        'current_odometer_miles': 650000,
        'total_engine_hours': 20000,
        'truck_age_years': 10,
        'anticipated_rv_miles_per_year': 40000
    }

    # 1. Generate spending dataframe array
    target_engine = 'Volvo_D13TC'
    spending_plan_df = finance_engine.generate_5year_spending_plan(target_engine, used_volvo_listing)
    
    # 2. TRIGGER THE UPGRADED VISUAL CHART EXPORT
    # Pass your variables to build the stamped text boxes and unique file name strings
    finance_engine.plot_5year_cash_burn(target_engine, used_volvo_listing, spending_plan_df, output_dir="financial_reports")


