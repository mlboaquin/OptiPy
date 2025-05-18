import numpy as np
from emissions_tracker import compare_emissions
from code_reformatter import refactor_code

# Original sample code
sample_code = """
def process_data():
    import pandas as pd
    import numpy as np
    
    # Create sample data
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })
    
    # Pandas operations that can be converted to NumPy
    mean_value = df.mean()  # Will be converted to np.mean(df)
    std_value = df.std()    # Will be converted to np.std(df)
    sorted_data = df.sort_values('A')  # Will be converted to np.sort(df)
    
    # List append example
    numbers = []
    for i in range(1000):
        numbers.append(i)

    # String formatting
    name = "Alice"
    age = 30
    message = f"Hello {name}, you are {age} years old"
    
    # Format example
    user = "Bob"
    place = "Python"
    greeting = "Welcome, {} to {}".format(user, place)
    
    return numbers, message, greeting, mean_value, std_value, sorted_data
"""

# Get reformatted code
reformatted_code, changes = refactor_code(sample_code)

if reformatted_code is None:
    print("Refactoring failed:")
    for error in changes:
        print(f"- {error}")
else:
    # Create function objects from the code strings
    exec(sample_code, globals())
    original_func = globals()['process_data']
    
    exec(reformatted_code, globals())
    reformatted_func = globals()['process_data']
    
    print("Comparing emissions between original and reformatted code:")
    print("\nReformatted code:")
    print(reformatted_code)
    
    print("\nChanges made in reformatted code:")
    for change in changes:
        print(f"- {change}")
        
    print("\nEmissions comparison:")
    compare_emissions(original_func, reformatted_func)