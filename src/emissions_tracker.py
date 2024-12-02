from codecarbon import EmissionsTracker
import time
import os
import sys
import inspect
import ast
import numba
import numpy as np

class CodeAnalyzer(ast.NodeVisitor):
    """Analyzes Python code to determine if it's numerical computing heavy"""
    def __init__(self):
        self.numpy_usage = 0
        self.math_operations = 0
        self.total_operations = 0
        
    def visit_Name(self, node):
        if node.id == 'np' or node.id == 'numpy':
            self.numpy_usage += 1
        self.total_operations += 1
        self.generic_visit(node)
        
    def visit_BinOp(self, node):
        self.math_operations += 1
        self.total_operations += 1
        self.generic_visit(node)
        
    def is_numerical_heavy(self):
        if self.total_operations == 0:
            return False
        # If more than 30% of operations are numerical/numpy-related
        return (self.numpy_usage + self.math_operations) / self.total_operations > 0.3

def analyze_code(source_code):
    """Analyzes the code to determine the best optimization strategy"""
    tree = ast.parse(source_code)
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)
    return analyzer.is_numerical_heavy()

def create_numba_optimizer(func):
    """Creates a Numba-optimized version of the input function"""
    try:
        # Create the optimized function
        optimized_func = numba.jit(nopython=True)(func)
        
        # Print the LLVM IR
        print("\nNumba LLVM IR:")
        print(optimized_func.inspect_llvm())
        
        # Print the Assembly
        print("\nNumba Assembly:")
        print(optimized_func.inspect_asm())
        
        return optimized_func
    except Exception as e:
        print(f"Numba optimization failed: {str(e)}")
        return func

def optimized_code(inefficient_func):
    """
    Analyzes the input function and chooses the best optimization strategy:
    - Numba for numerical computing
    Falls back to original function if optimization fails.
    """
    # Get the source code of the inefficient function
    source = inspect.getsource(inefficient_func)
    
    # Analyze the code
    is_numerical = analyze_code(source)
    
    if is_numerical:
        print("Detected numerical computing code - using Numba optimization")
        try:
            return create_numba_optimizer(inefficient_func)
        except Exception as e:
            print(f"Numba optimization failed: {str(e)}")
            return inefficient_func
    else:
        print("Detected general Python code - using original unoptimized function")
        return inefficient_func

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