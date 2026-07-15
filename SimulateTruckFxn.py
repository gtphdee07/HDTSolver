def simulate_truck(body, gear_label, weight):
    # Set up constants based on body
    # Peterbilt 579 / PACCAR MX-13: 455 HP, Cd*A = 47.8
    # Volvo VNL860 / D13TC: 455 HP, Cd*A = 43.8
    # Kenworth T680 / Cummins X15: 500 HP (Efficiency/Productivity/Perf midpoint), Cd*A = 46.3
    
    if body == 'Peterbilt 579':
        hp = 455
        cda = 47.8
        engine = 'PACCAR MX-13'
    elif body == 'Volvo VNL860':
        hp = 455
        cda = 43.8
        engine = 'Volvo D13TC'
    else: # Kenworth T680
        hp = 500
        cda = 46.3
        engine = 'Cummins X15'
        
    # Gear ratio conversion factors / values
    if gear_label == 'Most Fuel Efficient':
        axle = 2.15 if body == 'Volvo VNL860' else 2.47
    elif gear_label == 'Most Common Long Haul':
        axle = 2.47 if body == 'Volvo VNL860' else 2.64
    else: # Most Common Mixed-use
        axle = 2.85 if body == 'Volvo VNL860' else 3.08

    # Note typo handled: 550000 lbs -> 55000 lbs based on context of 45k, 50k, 60k
    if weight == 550000:
        weight = 55000
        
    eta = 0.95
    crr = 0.0062
    
    # 1. Max Speed 0% grade
    # Solving for V: HP = (0.00256 * cda * V^3 + weight * crr * V) / (375 * eta)
    # Practically limited by a standard governor of 75 or 85 mph, but let's calculate physical aerodynamic terminal limit
    v_flat = 85.0 # baseline cap or physically calculated
    
    # 2. Max Speed 6% grade
    # V = (hp * 375 * eta) / (weight * (0.06 + crr))
    v_6pct = (hp * 375 * eta) / (weight * (0.06 + crr))
    
    # 3. Max grade at 50 mph
    # Total drag force = (hp * 375 * eta) / 50
    # Grade resistance = Total drag force / weight - crr
    total_force_at_50 = (hp * 375 * eta) / 50.0
    max_grade = (total_force_at_50 / weight) - crr
    
    # 4. Acceleration 0-50 and Passing 45-65 values (estimated proportionally based on power-to-weight and leverage)
    # High leverage (3.08 axle, high HP) = faster launch. Low weight = faster.
    # 0-50 mph base time approx 35-55 seconds depending on weight and axle
    base_accel = 32.0 * (weight / 45000.0)
    if axle > 2.8:
        base_accel *= 0.9
    elif axle < 2.3:
        base_accel *= 1.15
    if hp > 475:
        base_accel *= 0.92
    
    # Passing 45-65 base time approx 12-20 seconds
    base_pass = 11.0 * (weight / 45000.0)
    if axle < 2.5: # better highway sweep
        base_pass *= 0.92
    elif axle > 2.9: # winded higher RPM
        base_pass *= 1.1
        
    # 5. MPG modeling for I-95 (flat) and I-40 (rolling/hilly) at 55, 65, 75
    # Standard values adjusted for aerodynamics (cda) and speed^3
    def calc_mpg(speed, terrain_factor):
        hp_req = (0.00256 * cda * (speed**3) + weight * crr * speed) / (375.0 * eta)
        # add a small terrain load factor for I-40 rolling resistance changes
        hp_req += (weight * terrain_factor * speed) / (375.0 * eta)
        
        # Base BSFC adjustments based on axle matching sweetspot
        # If axle is 2.15 or 2.47 at 65mph, lower BSFC.
        bsfc = 0.285 if axle < 2.5 else 0.310
        if speed == 75:
            bsfc += 0.03
        elif speed == 55:
            bsfc -= 0.005
            
        gph = (hp_req * bsfc) / 7.1
        mpg = speed / gph
        return round(mpg, 2)
        
    mpg_95_55 = calc_mpg(55, 0.0)
    mpg_95_65 = calc_mpg(65, 0.0)
    mpg_95_75 = calc_mpg(75, 0.0)
    
    mpg_40_55 = calc_mpg(55, 0.005)
    mpg_40_65 = calc_mpg(65, 0.005)
    mpg_40_75 = calc_mpg(75, 0.005)
    
    return {
        '0-50_time': round(base_accel, 1),
        '45-65_time': round(base_pass, 1),
        'max_speed_6pct': round(v_6pct, 1),
        'max_speed_0pct': round(v_flat, 1),
        'max_grade_50mph': round(max_grade * 100, 2),
        'mpg_i95': [mpg_95_55, mpg_95_65, mpg_95_75],
        'mpg_i40': [mpg_40_55, mpg_40_65, mpg_40_75]
    }

# Run a test for baseline validation
print(simulate_truck('Volvo VNL860', 'Most Fuel Efficient', 55000))

