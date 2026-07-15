import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure you have run: pip install pandas numpy matplotlib seaborn
sns.set_theme(style="whitegrid")

# =====================================================================
# GENERATE SIMULATED SURVEY DATAFRAME MATCHING OUR PIPELINE STRUCTURE
# =====================================================================
np.random.seed(42)

truck_models = ['Ford F-450 DRW HO', 'Kenworth T680 X15', 'Volvo VNL 860 D13TC']
axle_ratios = [2.15, 2.47, 2.64, 2.79, 3.08, 4.30]
payload_weights = [25000, 35000, 45000]
speeds = [55, 65, 75]
scenarios = ['I95_Fuel_Slasher', 'I70_Mountain_Conqueror']

records = []

# Populate structured mock rows that map flawlessly to our real physics variables
for truck in truck_models:
    # Restrict allowed axles per truck spec rule matrices
    if 'Ford' in truck:
        truck_axles = [4.30]
        curb_weight = 8600
        base_mpg = 8.5
    elif 'Volvo' in truck:
        truck_axles = [2.15, 2.47, 2.64]
        curb_weight = 18900
        base_mpg = 10.5
    else: # Kenworth
        truck_axles = [2.64, 2.79, 3.08]
        curb_weight = 18400
        base_mpg = 9.8

    for axle in truck_axles:
        for pw in payload_weights:
            total_w = curb_weight + pw
            
            # --- Scenario 1: I-95 Flat Land Cruise ---
            for sp in speeds:
                # Physics rule: mpg drops heavily as speed rises (aerodynamics)
                speed_penalty = (sp - 55) * 0.18 if 'Ford' not in truck else (sp - 55) * 0.12
                weight_penalty = (pw - 25000) * 0.00004
                axle_mod = (axle - 2.5) * 0.4 if 'Ford' not in truck else 0
                
                calculated_mpg = max(4.5, base_mpg - speed_penalty - weight_penalty - axle_mod)
                
                records.append({
                    'Truck_Model': truck, 'Axle_Ratio': str(axle), 'Trailer_Payload_lbs': pw,
                    'Route_Scenario': 'I95_Fuel_Slasher', 'Speed_MPH': sp, 'Calculated_MPG': round(calculated_mpg, 2),
                    'Max_Speed_6pct_Grade_MPH': round(65.0 - (total_w * 0.0004), 1) if 'Ford' not in truck else round(72.0 - (total_w * 0.0008), 1),
                    'Downhill_Req_Braking_HP': round(((total_w * 0.06 - total_w * 0.0062) * 45) / 375, 1)
                })

            # --- Scenario 2: I-70 Mountain Climb ---
            for sp in [35, 45]:  # Realistic mountain speeds
                weight_penalty = (pw - 25000) * 0.00006
                calculated_mpg = max(2.5, (base_mpg * 0.4) - weight_penalty)
                
                records.append({
                    'Truck_Model': truck, 'Axle_Ratio': str(axle), 'Trailer_Payload_lbs': pw,
                    'Route_Scenario': 'I70_Mountain_Conqueror', 'Speed_MPH': sp, 'Calculated_MPG': round(calculated_mpg, 2),
                    'Max_Speed_6pct_Grade_MPH': round(65.0 - (total_w * 0.0004), 1) if 'Ford' not in truck else round(72.0 - (total_w * 0.0008), 1),
                    'Downhill_Req_Braking_HP': round(((total_w * 0.06 - total_w * 0.0062) * 45) / 375, 1)
                })

df_tidy = pd.DataFrame(records)

# =====================================================================
# GRAPH 1: THE MULTI-SPEED FUEL SLASHER LINE PLOT (I-95 Flats)
# =====================================================================
plt.figure(figsize=(11, 6))

# Filter specifically for the standard 35,000 lbs trailer comparison vector
df_flat = df_tidy[(df_tidy['Route_Scenario'] == 'I95_Fuel_Slasher') & (df_tidy['Trailer_Payload_lbs'] == 35000)]

# Plot unique lines separating truck profiles by axle ratio styles
sns.lineplot(
    data=df_flat, x='Speed_MPH', y='Calculated_MPG', 
    hue='Truck_Model', style='Axle_Ratio', 
    markers=True, dashes=True, linewidth=2.5, palette='Set1'
)

plt.title('Graph 1: Aerodynamic Speed Penalty Matrix\n(Flat Highway Cruise at 35,000 lbs Payload)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Vehicle Cruising Speed (MPH)', fontsize=12)
plt.ylabel('Calculated Fuel Efficiency (MPG)', fontsize=12)
plt.xticks(speeds)
plt.legend(title='Vehicle Config Profiles', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# =====================================================================
# GRAPH 2: MOUNTAIN CLIMB VS. FLAT HIGHWAY TRADEOFF SCATTER
# =====================================================================
plt.figure(figsize=(10, 6))

# Filter out duplicate rows since mountain speed is static for the chassis config
df_tradeoff = df_tidy[(df_tidy['Speed_MPH'] == 65) & (df_tidy['Route_Scenario'] == 'I95_Fuel_Slasher')]

# Scatter configuration mapping out quadrants of business efficiency limits
sns.scatterplot(
    data=df_tradeoff, x='Max_Speed_6pct_Grade_MPH', y='Calculated_MPG',
    hue='Truck_Model', style='Axle_Ratio', size='Trailer_Payload_lbs',
    sizes=(40, 240), palette='Set1', alpha=0.85
)

plt.title('Graph 2: Fleet Performance Trade-Off Mapping Matrix\n(Mountain Climb Velocity vs. Flat Land Fuel Economy)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Maximum Attainable Speed Up a 6% Grade (MPH)', fontsize=12)
plt.ylabel('Cruising Fuel Efficiency at 65 MPH (MPG)', fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# =====================================================================
# GRAPH 4: DOWNHILL DESCENT CONTROL BRAKING CRITICAL THRESHOLDS
# =====================================================================
fig, ax = plt.subplots(figsize=(11, 6))

# Filter down to look cleanly at a single speed state across variable weight blocks
df_braking = df_tidy[(df_tidy['Speed_MPH'] == 45) & (df_tidy['Route_Scenario'] == 'I70_Mountain_Conqueror')].copy()
# Deduplicate our configuration structures
df_braking = df_braking.drop_duplicates(subset=['Truck_Model', 'Trailer_Payload_lbs'])

# Grouped bar configurations
sns.barplot(
    data=df_braking, x='Trailer_Payload_lbs', y='Downhill_Req_Braking_HP',
    hue='Truck_Model', palette='Set1', ax=ax, edgecolor='black', alpha=0.8
)

# Draw the explicit horizontal red structural safety thresholds for engine brake capacities
ax.axhline(y=250, color='red', linestyle='--', linewidth=2, label='Ford 6.7L HO Exhaust Brake Max (250 HP)')
ax.axhline(y=450, color='orange', linestyle='-.', linewidth=2, label='Cummins X15 Efficiency Jake Max (450 HP)')
ax.axhline(y=530, color='darkgreen', linestyle=':', linewidth=2, label='Volvo D13TC Engine Brake Max (530 HP)')

ax.set_title('Graph 4: Downhill Compression Brake Safety Limits\n(Continuous Horsepower Demanded to Hold 45 MPH Down a 6% Mountain Incline)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Trailer Payload Weight (lbs)', fontsize=12)
ax.set_ylabel('Required Continuous Retarding Power (HP)', fontsize=12)
ax.set_ylim(0, 600)

# Apply a background warning gradient block to flag danger thresholds to non-expert drivers
ax.axhspan(250, 600, color='red', alpha=0.04) # Shades the region where the Ford requires service brake assist

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

