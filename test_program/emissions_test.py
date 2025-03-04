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

    # Return the difference
    return emissions_inefficient - emissions_optimized