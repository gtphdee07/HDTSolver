
def test_volvo_ds():
    # Volvo I-Shift 12-Speed Automated Manual Transmission (AMT) Gear Ratio Profile
    volvo_ishift_ratios = {
        'Direct_Drive': {
            'model_series': 'AT Series (e.g., AT2612F)',
            'gears': {
                '1st':  14.94,
                '2nd':  11.73,
                '3rd':  9.04,
                '4th':  7.09,
                '5th':  5.54,
                '6th':  4.35,
                '7th':  3.44,
                '8th':  2.70,
                '9th':  2.08,
                '10th': 1.63,
                '11th': 1.28,
                '12th': 1.00  # Direct Drive Lockup (Peak Mechanical Efficiency)
            }
        },
        'Overdrive': {
            'model_series': 'ATO Series (e.g., ATO2612F)',
            'gears': {
                '1st':  11.73,
                '2nd':  9.21,
                '3rd':  7.09,
                '4th':  5.57,
                '5th':  4.35,
                '6th':  3.41,
                '7th':  2.70,
                '8th':  2.12,
                '9th':  1.63,
                '10th': 1.28,
                '11th': 1.00, # Direct Gear (Ideal for Mountain Climbing)
                '12th': 0.78  # Overdrive Gear (Ideal for Flat Highway Fuel Slashing)
            }
        },
        'Operational_Notes': {
            '1st_to_3rd': 'Heavy low-speed launching and construction site crawling.',
            '4th_to_6th': 'Low-speed city acceleration and suburban transitions.',
            '7th_to_9th': 'Regional road acceleration and mid-speed grade management.',
            '10th_to_12th': 'Interstate cruise, heavy hill-climbing, and downspeeding control.'
        }
    }
    # --- Practical Usage Example for your FleetPerformanceSweeper Class ---
    # To access a specific gear ratio during a simulated mountain downshift:
    target_gear = '11th'
    gear_ratio = volvo_ishift_ratios['Overdrive']['gears'][target_gear]

    print(f"Volvo Overdrive {target_gear} Gear Ratio: {gear_ratio}")


def get_gear(speed, rpm, final_drive, tire_revs):
    return (rpm * 60) / (speed * final_drive * tire_revs)

tire_revs = 529
final_drive = 2.95

print("At 65 MPH, 1250 RPM:", get_gear(65, 1250, final_drive, tire_revs))
print("At 60 MPH, 1250 RPM:", get_gear(60, 1250, final_drive, tire_revs))
print("At 45 MPH, 1250 RPM:", get_gear(45, 1250, final_drive, tire_revs))
print("At 65 MPH, 1200 RPM:", get_gear(65, 1200, final_drive, tire_revs))
print("At 65 MPH, 1150 RPM:", get_gear(65, 1150, final_drive, tire_revs))



def get_DemandHP(velocityMPH, gvw, cd_A, grade_as_percent, eta=0.95,crr=0.0062):
    # Truck Model: 2024 Kenworth T680
        # Drag Coefficient (Cd) : 0.44 to 0.46
        # Front Area (A) : 9.57  m^2 (103.1 ft^2))
        # Combined Cd*A : 4.2 m^2 (45.2 ft^2) 46.3
        # Truck Weight (GVW) : 25,000 to 80,000 lb
    # Truck Model: Volvo VNL 860
        # Drag Coefficient (Cd) : 0.42 to 0.40
        # Front Area (A) : 9.57  m^2 (103.1 ft^2))
        # Combined Cd*A : 3.5 m^2 (37.7 ft^2) 43.8
        # Truck Weight (GVW) : 25,000 to 80,000 lb
    # Truck Model: Peterbilt 579
        # Drag Coefficient (Cd) : 0.45 to 0.47
        # Front Area (A) : 9.66  m^2 (104 ft^2))
        # Combined Cd*A : 3.5 m^2 (37.7 ft^2) 47.8
        # Truck Weight (GVW) : 25,000 to 80,000 lb

    # Aero resistance
    # 0.00256 The physics constant that accounts for standard air density at sea level ( 0.075 lb/ft^3 )and converts miles-per-hour squared into pounds of force.
    R_aero = 0.00256 * cd_A * (velocityMPH ** 2)
    # Rolling resistance
    # Coefficient of rolling resistance (CRR) is a dimensionless number that represents the rolling resistance of a tire. It is typically between 0.005 and 0.01 for truck tires.
    R_rolling = gvw * crr
    # Grade resistance
    # Grade resistance is the force required to overcome the gravitational pull when driving uphill. It is calculated as the weight of the vehicle multiplied by the sine of the grade angle. For small angles, sin(grade) ≈ grade (in decimal form).

    R_grade = gvw * grade_as_percent / 100
    Total_R = R_aero + R_rolling + R_grade
    HP_demand = (Total_R * velocityMPH) / (375 * eta)
    print(f"R_aero: {R_aero}")
    print(f"R_rolling: {R_rolling}")
    print(f"Total_R: {Total_R}")
    print(f"HP_demand: {HP_demand}")
    return HP_demand

import numpy as np

def calculate_speed(weight, hp, grade=0.06, efficiency=0.94):
    c3 = 0.01536 / 375
    c1 = weight * (grade + 0.005) / 375
    c0 = -hp * efficiency
    roots = np.roots([c3, 0, c1, c0])
    return [r.real for r in roots if np.isreal(r) and r > 0][0]

hp = 500
print("If GVW is exactly 25k, 35k, 40k:")
print({25000: calculate_speed(25000, hp), 35000: calculate_speed(35000, hp), 40000: calculate_speed(40000, hp)})

print("If Payload is 25k, 35k, 40k (adding 32k truck/trailer weight = 57k, 67k, 72k GVW):")
print({25000: calculate_speed(57000, hp), 35000: calculate_speed(67000, hp), 40000: calculate_speed(72000, hp)})


def calculate_axel_ratio(cruise_speed=65, top_gear_ratio=0.77, target_rpm=1150, tire_revs_per_mile=520):


    # Calculate the exact axle ratio for a 65 MPH baseline
    # Formula: RPM = (Speed * Gear_Ratio * Axle_Ratio * Tire_Rev_Per_Mile) / 60
    # Therefore: Axle_Ratio = (RPM * 60) / (Speed * Gear_Ratio * Tire_Rev_Per_Mile)

    #speed = 65
    #target_rpm = 1150  # Ideal sweet spot RPM for Cummins X15
    #gear_ratio = 0.77  # Eaton Cummins Endurant 12th gear overdrive ratio
    #tire_revs_per_mile = 520  # Standard low-profile drive tires calculated earlier

    axle_ratio = (target_rpm * 60) / (cruise_speed * top_gear_ratio * tire_revs_per_mile)
    print(f"Calculated Axle Ratio: {axle_ratio:.3f}")
    return axle_ratio

def calculate_tire_rev_per_mile_inches(tire_diameter_inches):
    # Convert tire diameter from inches to feet
    tire_diameter_feet = tire_diameter_inches / 12
    # Calculate the circumference of the tire in feet
    tire_circumference_feet = np.pi * tire_diameter_feet
    # Calculate the number of tire revolutions per mile
    tire_revs_per_mile = 5280 / tire_circumference_feet
    print(f"Tire Revolutions per Mile: {tire_revs_per_mile:.2f}")
    return tire_revs_per_mile

def calculate_tire_rev_per_mile_size(Tire_Size):
    # Tire size format: "11R22.5" or "295/75R22.5"
    if "R" in Tire_Size:
        if "/" in Tire_Size:
            # Format: "295/75R22.5"
            width, aspect_ratio, rim_diameter = Tire_Size.split("/")
            rim_diameter = rim_diameter[1:]  # Remove the 'R'
            width = float(width)
            aspect_ratio = float(aspect_ratio)
            rim_diameter = float(rim_diameter)
            # Calculate tire diameter in inches
            tire_diameter_inches = (width * (aspect_ratio / 100) * 2) + rim_diameter
        else:
            # Format: "11R22.5"
            tire_diameter_inches = float(Tire_Size.split("R")[1]) + (float(Tire_Size.split("R")[0]) * 2)
    else:
        raise ValueError("Invalid tire size format")
    
    return calculate_tire_rev_per_mile_inches(tire_diameter_inches)

def calculate_fuel_burn_rate(demand_hp, BSFC=0.45):
    # BSFC: Brake Specific Fuel Consumption in lb/hp-hr
    # Fuel burn rate in gallons per hour (GPH)
    fuel_burn_rate_gph = (demand_hp * BSFC) / 7.1   # 7.1 lb/gal for diesel
    print(f"Fuel Burn Rate: {fuel_burn_rate_gph:.2f} GPH")
    return fuel_burn_rate_gph

def calculate_top_speed_up_a_hill():
    # Given variables
    hp = 455
    efficiency = 0.94
    grade = 0.0600
    c_rr = 0.0062
    total_resistance_factor = grade + c_rr
    gvw = 55000
    axle_ratio = 2.15
    tires_rev_per_mile = 529

    # Part 1: Physics Top Speed Limit
    # V = (HP * 375 * eta) / (GVW * Total Resistance Factor)
    numerator_v = hp * 375 * efficiency
    denominator_v = gvw * total_resistance_factor
    v_max = numerator_v / denominator_v

    # Part 2: Gearing Test
    # We want to see what gear keeps us at or below v_max. 
    # Let's find the gear ratios for Volvo I-Shift Overdrive from previous prompt:
    # 8th: 2.12
    # 9th: 1.63
    # 10th: 1.28
    # 11th: 1.00
    # 12th: 0.78

    gear_ratios = {
        "12th": 0.78,
        "11th": 1.00,
        "10th": 1.28,
        "9th": 1.63,
        "8th": 2.12
    }

    results = {}
    for gear, ratio in gear_ratios.items():
        # RPM at v_max for this gear
        rpm = (v_max * ratio * axle_ratio * tires_rev_per_mile) / 60
        results[gear] = rpm

    print(f"V_max: {v_max:.2f} MPH")
    for gear, rpm in results.items():
        print(f"{gear} gear ({gear_ratios[gear]} ratio): RPM = {rpm:.0f}")
   
       
    return results
