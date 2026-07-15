    def plot_graph_1_fuel_slasher(self, tidy_df, preferred_payload=35000):
        """
        Generates the Multi-Speed Fuel Slasher Line Plot (I-95 Flats).
        """
        available_payloads = tidy_df['Trailer_Payload_lbs'].unique()
        if len(available_payloads) == 0:
            print("Visualizer Warning: No valid data found for Graph 1.")
            return None
            
        # DYNAMIC SCALAR FIX: Slice index [0] to extract a pure scalar integer if fallback triggers
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads[0]

        df_flat = tidy_df[
            (tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher') & 
            (tidy_df['Trailer_Payload_lbs'] == target_payload)
        ]
        
        if df_flat.empty:
            print(f"Visualizer Warning: No valid I-95 cruise rows found for payload {target_payload} lbs.")
            return None

        plt.figure(figsize=(11, 6))
        sns.lineplot(
            data=df_flat, x='Speed_MPH', y='Calculated_MPG', 
            hue='Truck_Model', style='Axle_Ratio', 
            markers=True, dashes=True, linewidth=2.5, palette=self.palette
        )

        plt.title(f'Graph 1: Aerodynamic Speed Penalty Corridor Matrix\n(Flat Highway Cruise at {target_payload:,} lbs Payload)', fontweight='bold', pad=15)
        plt.xlabel('Vehicle Cruising Speed (MPH)', labelpad=10)
        plt.ylabel('Calculated Fuel Efficiency (MPG)', labelpad=10)
        
        unique_speeds = sorted(df_flat['Speed_MPH'].unique())
        plt.xticks(unique_speeds)
        plt.legend(title='Vehicle Config Profiles', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_1_fuel_slasher.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_5_route_cost_split(self, tidy_df, preferred_payload=35000, diesel_price_per_gal=4.00, def_price_per_gal=5.00):
        """
        Generates the Operating Cost Split Stacked Bar Chart.
        """
        available_payloads = tidy_df['Trailer_Payload_lbs'].unique()
        if len(available_payloads) == 0:
            print("Visualizer Warning: No valid data found for Graph 5 operating costs.")
            return None
            
        # DYNAMIC SCALAR FIX: Slice index [0] to extract a pure scalar integer if fallback triggers
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads[0]
        
        df_cost = tidy_df[(tidy_df['Speed_MPH'] == 65) & (tidy_df['Trailer_Payload_lbs'] == target_payload)].copy()
        
        if df_cost.empty:
            available_speeds = tidy_df[tidy_df['Trailer_Payload_lbs'] == target_payload]['Speed_MPH'].unique()
            if len(available_speeds) == 0:
                print(f"Visualizer Warning: Missing data rows for payload {target_payload} lbs in Graph 5.")
                return None
            target_speed = available_speeds[0]
            df_cost = tidy_df[(tidy_df['Speed_MPH'] == target_speed) & (tidy_df['Trailer_Payload_lbs'] == target_payload)].copy()

        df_cost['Diesel_Cost_Per_1k_Miles'] = (1000 / df_cost['Calculated_MPG']) * diesel_price_per_gal
        df_cost['DEF_Cost_Per_1k_Miles'] = ((1000 / df_cost['Calculated_MPG']) * 0.04) * def_price_per_gal
        df_cost['Config_Label'] = df_cost['Truck_Model'] + " (" + df_cost['Axle_Ratio'].astype(str) + " Axle)"

        df_agg = df_cost.groupby('Config_Label', as_index=False).mean(numeric_only=True)

        plt.figure(figsize=(12, 6))
        sns.barplot(data=df_agg, x='Config_Label', y='Diesel_Cost_Per_1k_Miles', color='darkblue', alpha=0.85, label='Diesel Fuel Cost')
        sns.barplot(data=df_agg, x='Config_Label', y='DEF_Cost_Per_1k_Miles', color='cyan', alpha=0.6, label='DEF Fluid Cost', bottom=df_agg['Diesel_Cost_Per_1k_Miles'])

        plt.title(f'Graph 5: Route Operating Fluid Cost Comparison\n(Projected Expenses Per 1,000 Miles at {df_cost["Speed_MPH"].iloc[0]} MPH / {target_payload:,} lbs Payload)', fontweight='bold', pad=15)
        plt.xlabel('Vehicle Configuration Profile')
        plt.ylabel('Operating Fluid Cost ($ per 1,000 Miles)')
        plt.xticks(rotation=15, ha='right')
        plt.legend(title='Fluid Breakdown', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        save_path = os.path.join(self.output_dir, "graph_5_route_cost_split.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        return save_path

    def plot_graph_8_speed_penalty_ROI(self, tidy_df, preferred_payload=35000, generate_individual_profiles=False):
        """
        Generates the Fleet Velocity ROI Return Matrix (Graph 8).
        """
        df_flat = tidy_df[tidy_df['Route_Scenario'] == 'I95_Fuel_Slasher'].copy()
        if df_flat.empty:
            print("Visualizer Warning: Missing long-haul data rows for Graph 8.")
            return None

        available_payloads = df_flat['Trailer_Payload_lbs'].unique()
        
        # DYNAMIC SCALAR FIX: Slice index [0] to extract a pure scalar integer if fallback triggers
        target_payload = preferred_payload if preferred_payload in available_payloads else available_payloads[0]
        df_flat = df_flat[df_flat['Trailer_Payload_lbs'] == target_payload].copy()

        df_flat['Config_Profile'] = df_flat['Truck_Model'] + " (" + df_flat['Axle_Ratio'].astype(str) + " Axle)"
        df_flat['Annual_Fuel_Bill_Dollars'] = (100000 / df_flat['Calculated_MPG']) * 4.00
        df_flat['Annual_Windshield_Hours'] = 100000 / df_flat['Speed_MPH']
        df_flat = df_flat.sort_values('Speed_MPH')

        fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
        
        sns.lineplot(data=df_flat, x='Speed_MPH', y='Annual_Fuel_Bill_Dollars', hue='Config_Profile', marker='o', linewidth=2.5, palette=self.palette, ax=axes[0])
        axes[0].set_title('A: Annual Fuel Expenditure Lifecycle\n(Based on 100,000 Annual Miles at $4.00/gal)', fontsize=11, fontweight='semibold')
        axes[0].set_xlabel('Target Cruising Speed (MPH)', labelpad=10)
        axes[0].set_ylabel('Annual Fuel Expense ($)', labelpad=10)
        axes[0].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
        axes[0].set_xticks(sorted(df_flat['Speed_MPH'].unique()))
        if axes[0].get_legend(): axes[0].get_legend().remove()

        sns.lineplot(data=df_flat, x='Speed_MPH', y='Annual_Windshield_Hours', hue='Config_Profile', marker='s', linewidth=2.5, linestyle='--', palette=self.palette, ax=axes[1])
        axes[1].set_title('B: Annual Driver Windshield Time\n(Total Clock Hours Required to Complete 100,000 Miles)', fontsize=11, fontweight='semibold')
        axes[1].set_xlabel('Target Cruising Speed (MPH)', labelpad=10)
        axes[1].set_ylabel('Driver Windshield Time (Hours)', labelpad=10)
        axes[1].get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} hrs".format(int(x))))
        axes[1].set_xticks(sorted(df_flat['Speed_MPH'].unique()))
        
        plt.suptitle(f'Graph 8: Fleet Velocity ROI Return Matrix\n(Comparative Multi-Line Sweep at {target_payload:,} lbs Trailer Payload)', fontweight='bold', y=0.98)
        
        if axes[1].get_legend(): axes[1].get_legend().remove()
        axes[1].legend(title='Vehicle Config Profile', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        master_save_path = os.path.join(self.output_dir, "graph_8_fleet_roi_comparison.png")
        plt.savefig(master_save_path, dpi=300)
        plt.close()
        print(f"[Visualizer Master Log]: Compiled multi-line comparison sheet -> '{master_save_path}'")

        if generate_individual_profiles:
            unique_configs = df_flat['Config_Profile'].unique()
            for config in unique_configs:
                df_sub = df_flat[df_flat['Config_Profile'] == config]
                fig, ax1 = plt.subplots(figsize=(10, 6))
                
                color = 'tab:red'
                ax1.set_xlabel('Target Cruising Speed (MPH)', fontsize=11, labelpad=10)
                ax1.set_ylabel('Annual Fuel Expense ($)', color=color, fontsize=11, labelpad=10)
                line1 = ax1.plot(df_sub['Speed_MPH'], df_sub['Annual_Fuel_Bill_Dollars'], color=color, marker='o', linewidth=3, label='Annual Fuel Bill ($)')
                ax1.tick_params(axis='y', labelcolor=color)
                ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
                ax1.grid(True, linestyle=':', alpha=0.6)

                ax2 = ax1.twinx()  
                color = 'tab:blue'
                ax2.set_ylabel('Annual Driver Windshield Hours (Hrs)', color=color, fontsize=11, labelpad=10)
                line2 = ax2.plot(df_sub['Speed_MPH'], df_sub['Annual_Windshield_Hours'], color=color, marker='s', linewidth=3, linestyle='--', label='Windshield Time (Hours)')
                ax2.tick_params(axis='y', labelcolor=color)
                ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,} hrs".format(int(x))))

                lines = line1 + line2
                labels = [l.get_label() for l in lines]
                ax1.legend(lines, labels, loc='upper center')

                plt.title(f'Isolated Velocity ROI Cross-Plot\nVehicle Target: {config}', fontweight='bold', pad=15)
                fig.tight_layout()
                
                file_slug = config.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
                sub_save_path = os.path.join(self.output_dir, f"graph_8_roi_{file_slug}.png")
                plt.savefig(sub_save_path, dpi=300)
                plt.close()
                
        return master_save_path
