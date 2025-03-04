import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from emissions_test import compare_emissions
from code_reformatter import refactor_code
import statistics

def create_test_function(code_str):
    """Creates a function from a code string that can be executed"""
    namespace = {}
    
    # Prepare the code string by properly indenting it
    indented_code = '\n'.join('        ' + line for line in code_str.split('\n'))
    
    # Create the function definition with the indented code
    wrapped_code = (
        'def test_function():\n'
        '    try:\n'
        f'{indented_code}\n'
        '    except Exception as e:\n'
        '        pass  # Silently handle any runtime errors'
    )
    
    try:
        # Execute the wrapped code
        exec(wrapped_code, namespace)
        return namespace['test_function']
    except Exception as e:
        print(f"Error creating function: {e}")
        return None

def test_code_emissions():
    # Load code snippets
    with open('src/test_program/pandas_numpy.json', 'r') as f:
        code_snippets = json.load(f)

    emission_differences = []
    successful_tests = 0
    failed_tests = 0

    for i, code in enumerate(code_snippets, 1):
        print(f"\nTesting snippet {i}/{len(code_snippets)}")
        
        # Create function from original code
        original_func = create_test_function(code)
        
        # Refactor the code
        refactored_code, changes = refactor_code(code)
        if refactored_code is None:
            print(f"Snippet {i}: Refactoring failed - {changes}")
            failed_tests += 1
            continue

        # Create function from refactored code
        refactored_func = create_test_function(refactored_code)

        if original_func is None or refactored_func is None:
            print(f"Snippet {i}: Function creation failed")
            failed_tests += 1
            continue

        try:
            # Compare emissions
            emission_diff = compare_emissions(original_func, refactored_func)
            emission_differences.append(emission_diff)
            successful_tests += 1
            print(f"Snippet {i}: Emission difference: {emission_diff:.10f} CO2eq")
            
            # Print changes made during refactoring
            if changes:
                print("Changes made:")
                for change in changes:
                    print(f"  - {change}")
                
        except Exception as e:
            print(f"Snippet {i}: Error during emission comparison - {e}")
            failed_tests += 1

    # Calculate statistics
    if emission_differences:
        avg_difference = statistics.mean(emission_differences)
        median_difference = statistics.median(emission_differences)
        std_dev = statistics.stdev(emission_differences) if len(emission_differences) > 1 else 0
        
        print("\nResults Summary:")
        print(f"Successful tests: {successful_tests}")
        print(f"Failed tests: {failed_tests}")
        print(f"Average emission difference: {avg_difference:.10f} CO2eq")
        print(f"Median emission difference: {median_difference:.10f} CO2eq")
        print(f"Standard deviation: {std_dev:.10f} CO2eq")
        print(f"Total positive improvements: {sum(1 for x in emission_differences if x > 0)}")
        print(f"Total negative impacts: {sum(1 for x in emission_differences if x < 0)}")
    else:
        print("\nNo successful tests to analyze")

if __name__ == "__main__":
    test_code_emissions()