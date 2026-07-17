# Heavy Equipment & RV Fleet Simulation Engine

An enterprise-grade, decoupled vehicle dynamics physics simulator and financial operations-and-maintenance (O&M) forecaster. Built specifically to assist non-expert buyers and luxury RV owners, this tool models the exact mechanical headroom, safety boundaries, fuel trade-offs, and multi-year calendar spending budgets of heavy towing platforms. It compares Class 8 commercial tractors (e.g., Volvo VNL 860, Kenworth T680, Freightliner Cascadia) side-by-side with Class 4/5 medium-duty pickup trucks (e.g., Ford F-450/F-600, Ram 5500, GM 5500).

---

## 🚀 System Architecture & Key Capabilities

Unlike generic simulation matrices, this tool runs continuous, force-balance energy equations rooted in real-world fluid dynamics and vehicle mechanics.

*   **Fluid & Aerodynamic Force Balancing**: Computes dynamic rolling resistance lines (\(C_{rr}\)), terrain grade forces, and exponential aerodynamic velocity decay curves (\(C_d \times A \times V^2\)).
*   **Geometric BSFC Island Mapping**: Models a 4-wall fuel efficiency map that applies strict penalty curves if cruising RPM or engine load floats outside an engine's optimal Brake Specific Fuel Consumption window.
*   **Dynamic Headroom Metrics**: Replaces abstract stability factors with precise calculation boundaries:
    *   *Speed Delta Cushion (Δ V)*: The exact road speed you can drop in top gear before a mandatory transmission downshift is triggered.
    *   *Incline Delta Cushion (Δ θ)*: The precise percentage grade change a truck can absorb before exhausting its reserve torque and gear-hunting.
*   **Sawtooth Mountain Shifting Engine**: Simulates a 12-speed or 10-speed automated transmission downshift pacing loop (12 → 1) on severe 6% inclines across a dense 2 MPH resolution sweep, capping terminal climbing speeds (\(V_{\text{max\_6\%}}\)) dynamically based on actual wheel horsepower.
*   **Phase 3 Suspension Safety Check**: Models a 15% fifth-wheel/gooseneck vertical pin loading multiplier from the RV's total trailer weight. It fires a console warning if the pin weight consumes more than 95% of the truck's available Gross Vehicle Weight Rating (GVWR) buffer, outputting the exact structural tipping point.
*   **Idling Wear Correction Factor**: Evaluates used vehicles based on total operational engine hours vs. odometer mileage (calibrating true engine wear at 30 miles per idle hour) to catch heavily worn engines.

---

## 📁 Repository File Structure

The project is strictly decoupled into independent, highly single-responsible modules using a shared-memory singleton pattern to isolate memory space boundaries cleanly:

```text
├── registries/                     # Local temporary database backup path
├── executive_presentation_charts/  # Compiled high-resolution performance plots (.png)
├── financial_reports/              # Parameterized 5-year O&M cash burn graphs (.png)
├── fleet_state.py                  # Singleton Source of Truth (holds active global dictionaries)
├── excel_loader.py                 # Dynamic column-oriented vertical Excel sheet parsing engine
├── truck_simulator.py              # Main calculation execution module (Grid Manager & Physics loops)
├── fleet_visualizer.py             # Supervisor Graphics Class (Renders Graphs 1, 2, 3, 4, 5, 6, 7, and 8)
├── fleet_finance_engine.py         # Standalone secondary script for specific unit 5-year calendar budgeting
├── JSONToExcelConverter.py         # Data migration script transforming old text blocks to Columnar Excel
└── Fleet_Equipment_Database.xlsx   # User-facing columnar master database workbook
```

---

## 🛠️ Data Architecture (How to Modify and Add Trucks)

The data ingestion layer is entirely decoupled from the Python code. **You do not need to edit script files to add new trucks.** All equipment parameters are managed inside a human-friendly, vertical columnar spreadsheet named `Fleet_Equipment_Database.xlsx`.

### Adding a New Vehicle
1. Open `Fleet_Equipment_Database.xlsx`.
2. Go to the respective tab: `Trucks_Chassis`, `Engines`, or `Transmissions`.
3. Add a new column to the right of the existing data blocks.
4. Set the header row to a unique underscored string (e.g., `Dodge_Ram_5500_HD`).
5. Fill out the spec fields vertically matching the parameter rows exactly.
6. For trucks, assign the allowed rear axles cleanly across the numbered fields (`Rear_Axle_Ratio_1`, `Rear_Axle_Ratio_2`), leaving trailing slots blank.

---

## 📊 Generating Executive Presentation Reports

### 1. The Performance & Selection Model (`truck_simulator.py`)
Used during the research stage to compare multiple combinations of truck brands, payload capacities, and axle sets across flat long-haul (I-95), rolling hill (I-40), and severe mountain grade (I-70) corridors.

**To Run:**
Configure your sweeping profile at the bottom of `truck_simulator.py` and execute the file:
```python
user_request = {
    'chassis': ['Volvo_VNL_860', 'Kenworth_T680_NextGen', 'Ford_F450_Pickup'],
    'engine': ['ALL_VALID'],
    'transmission': ['ALL_VALID'],
    'axle_ratio': ['ALL_VALID'],
    'trailer_payload_lbs':,
    'route_corridor': ['I95_Fuel_Slasher', 'I40_Midwest_Rhythm', 'I70_Mountain_Conqueror']
}
```
**Outputs:** 
Generates an aggregated data workbook `Fleet_Executive_Decision_Matrix.xlsx` alongside eight standalone high-resolution charts inside `executive_presentation_charts/`:
*   **Graph 1: Aerodynamic Speed Penalty Corridor Plot** (Cruising speed vs. fuel drop).
*   **Graph 2: Fleet Performance Trade-Off Scatter** (Mountain climb speed vs. flat highway economy quadrants).
*   **Graph 3: Kinematics Responsiveness Bars** (0–50 MPH launch and 45–65 MPH passing sprint times in seconds).
*   **Graph 4: Downhill Brake Safety Limits** (Continuous braking horsepower demanded against engine brake capacity limits).
*   **Graph 5: Route Operating Fluid Cost Splits** (Stacked Diesel vs. DEF dollar expenditures per 1,000 miles).
*   **Graph 6: Transmission Headroom Cushions** (Side-by-side velocity delta and incline delta buffers before automatic shifting).
*   **Graph 7: Real Mountain Climb Shifting Sawtooth Map** (Continuous 2 MPH resolution engine RPM behavior across gear drops).
*   **Graph 8: Fleet Velocity ROI Return Matrix** (Windshield hours saved vs. cash burned per 100,000 miles).

### 2. The Specific Unit Audit Model (`fleet_finance_engine.py`)
An independent script executed once a specific vehicle listing has been selected on the used market. It calculates a chronological, 5-year calendar operations and maintenance spending forecast.

**To Run:**
Configure the specific listing data at the bottom of `fleet_finance_engine.py` and run:
```python
used_listing = {
    'current_odometer_miles': 650000,
    'total_engine_hours': 20000,
    'truck_age_years': 10,
    'anticipated_rv_miles_per_year': 40000
}
# Target specific engine from your spreadsheet tab
spending_df = finance_engine.generate_5year_spending_plan('Volvo_D13TC', used_volvo_listing)
```
**Outputs:**
Generates a year-by-year budget table tracking routine fluid checks, top-end valve overhauls, DPF ash cleanings, and clutch refreshes. It exports a uniquely parameterized chart named `cashburn_<chassis>_<age>_<mileage>_<mpy>.png` inside `financial_reports/` that features a visual **"Listing Blueprint Box"** metadata stamp and overlays specific warning annotations over critical expenditure years.

---

## 🤖 AI Data Sourcing Telemetry Layer

To gather hyper-specific equipment parameters without wading through thousands of manufacturer pages, use the pre-programmed **AI Asset Harvester Specification Prompt** found inside the repository's documentation directory. 

Simply copy the prompt template, insert your target vehicle name, paste it to an AI engine, and it will return clean vertical markdown text tables that line up with your Excel rows, allowing for easy copy-pasting straight into your active fleet sheet.

---

## 🛠️ Development & Engineering Attributions

This full-stack codebase was built using an iterative, adaptive collaborative pipeline between a domain-expert human fleet designer and a highly structured AI collaborator.

*   **Human Lead / Product Owner**: Engineered the physical parameters, defined the custom RV operational scenarios, restructured the vertical database schema formatting rules, and directed the dynamic headroom and dynamic braking safety logic upgrades.
*   **AI Collaborator**: Architected the software infrastructure patterns, wrote the multi-file singleton object-oriented loading logic, derived the mechanical calculations for fluid force vectors and BSFC islands, and developed the custom Matplotlib/Seaborn visualization reporting suites.
*   **Environment Prerequisites**: 
    ```bash
    pip install pandas numpy matplotlib seaborn openpyxl
    ```

---
*Developed as an open, future-proof asset tracking framework for the recreational vehicle towing community.*
