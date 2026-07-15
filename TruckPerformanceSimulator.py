import pandas as pd
import numpy as np

class TruckPerformanceSimulator:
    def __init__(self):
        # Truck Specs: [Horsepower, Aero Constant (Cd * A)]
        self.truck_profiles = {
            'Peterbilt 579': {'hp': 455, 'cda': 47.8, 'engine': 'PACCAR MX-13'},
            'Volvo VNL860': {'hp': 455, 'cda': 43.8, 'engine': 'Volvo D13TC'},
            'Kenworth T680': {'hp': 500, 'cda': 46.3, 'engine': 'Cummins X15'}
        }
        
        self.drivetrain_efficiency = 0.95
        self.rolling_resistance_coef = 0.0062
        self.fuel_density_lbs_gal = 7.1

    def run_iteration(self, body, gear_label, weight):
        # Data correction safety rule for input typos
        if weight > 100000:
            weight = weight / 10.0
            
        specs = self.truck_profiles[body]
        hp = specs['hp']
        cda = specs['cda']
        
        # Determine axle ratio assigned based on build strategies
        if gear_label == 'Most Fuel Efficient':
            axle = 2.15 if body == 'Volvo VNL860' else 2.47
        elif gear_label == 'Most Common Long Haul':
            axle = 2.47 if body == 'Volvo VNL860' else 2.64
        else: # Most Common Mixed-use
            axle = 2.85 if body == 'Volvo VNL860' else 3.08

        # Grade calculations
        v_6pct = (hp * 375 * self.drivetrain_efficiency) / (weight * (0.06 + self.rolling_resistance_coef))
        total_force_at_50 = (hp * 375 * self.drivetrain_efficiency) / 50.0
        max_grade_at_50 = (total_force_at_50 / weight) - self.rolling_resistance_coef
        
        # Kinematics estimates based on power-to-weight and mechanical leverage
        base_accel = 32.0 * (weight / 45000.0)
        if axle > 2.8: base_accel *= 0.9
        elif axle < 2.3: base_accel *= 1.15
        if hp > 475: base_accel *= 0.92
            
        base_pass = 11.0 * (weight / 45000.0)
        if axle < 2.5: base_pass *= 0.92
        elif axle > 2.9: base_pass *= 1.1

        # Fuel burn mapping method using BSFC curves
        def calculate_mpg(speed, terrain_rolling_factor):
            hp_req = (0.00256 * cda * (speed**3) + weight * self.rolling_resistance_coef * speed) / (375.0 * self.drivetrain_efficiency)
            hp_req += (weight * terrain_rolling_factor * speed) / (375.0 * self.drivetrain_efficiency)
            
            bsfc = 0.285 if axle < 2.5 else 0.310
            if speed == 75: bsfc += 0.030
            elif speed == 55: bsfc -= 0.005
                
            gph = (hp_req * bsfc) / self.fuel_density_lbs_gal
            return round(speed / gph, 2)

        return {
            'Truck Body': body,
            'Gear Spec': gear_label,
            'Axle Ratio': axle,
            'Weight (lbs)': int(weight),
            '0-50 MPH (s)': round(base_accel, 1),
            '45-65 MPH Pass (s)': round(base_pass, 1),
            'Max Speed 6% Grade (MPH)': round(v_6pct, 1),
            'Max Grade at 50MPH (%)': round(max_grade_at_50 * 100, 2),
            'I-95 MPG (55/65/75)': [calculate_mpg(55, 0.0), calculate_mpg(65, 0.0), calculate_mpg(75, 0.0)],
            'I-40 MPG (55/65/75)': [calculate_mpg(55, 0.005), calculate_mpg(65, 0.005), calculate_mpg(75, 0.005)]
        }

# Execution Block
simulator = TruckPerformanceSimulator()
baseline_result = simulator.run_iteration('Volvo VNL860', 'Most Fuel Efficient', 55000)

# Display Formatted Results
for key, value in baseline_result.items():
    print(f"{key}: {value}")

