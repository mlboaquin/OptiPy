from codecarbon import EmissionsTracker
import time
import os
import sys

def compare_emissions(inefficient_func, optimized_func):
    # Inefficient code
    tracker_inefficient = EmissionsTracker(log_level="error", save_to_file=False)
    tracker_inefficient.start()

    start_time_inefficient = time.time()
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull  
        inefficient_func()
        sys.stdout = sys.__stdout__ 
    end_time_inefficient = time.time()

    emissions_inefficient = tracker_inefficient.stop()
    energy_inefficient = tracker_inefficient.final_emissions_data.energy_consumed
    execution_time_inefficient = end_time_inefficient - start_time_inefficient

    # Optimized code
    tracker_optimized = EmissionsTracker(log_level="error", save_to_file=False)
    tracker_optimized.start()

    start_time_optimized = time.time()
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull 
        optimized_func()
        sys.stdout = sys.__stdout__ 
    end_time_optimized = time.time()

    emissions_optimized = tracker_optimized.stop()
    energy_optimized = tracker_optimized.final_emissions_data.energy_consumed
    execution_time_optimized = end_time_optimized - start_time_optimized

    # Print results
    print(f"===================== INEFFICIENT CODE =====================")
    print(f"Total carbon emissions: \t{emissions_inefficient:.10f} kg CO2e")
    print(f"Energy consumed: \t\t{energy_inefficient:.10f} kWh")
    print(f"Execution time: \t\t{execution_time_inefficient:.2f} seconds\n")

    print(f"====================== OPTIMIZED CODE ======================")
    print(f"Total carbon emissions: \t{emissions_optimized:.10f} kg CO2e")
    print(f"Energy consumed: \t\t{energy_optimized:.10f} kWh")
    print(f"Execution time: \t\t{execution_time_optimized:.2f} seconds\n")

    print(f"========================= RESULTS =========================")
    emission_difference = emissions_inefficient - emissions_optimized
    print(f"Carbon emissions reduced by optimization: {emission_difference:.10f} kg CO2e")

    if emission_difference > 0:
        print("Interpretation: Optimized code produces less carbon emissions.")
    else:
        print("Interpretation: Inefficient code produces less carbon emissions.")