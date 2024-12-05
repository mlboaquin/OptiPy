import requests
import json

def test_optimization():
    # Test code (no function definition needed - it will be wrapped automatically)
    test_code = """
numbers = []
for i in range(1000):
    numbers.append(i)

name = "Alice"
age = 30
message = f"Hello {name}, you are {age} years old"
"""

    # Send request to the server
    response = requests.post(
        'http://localhost:5000/optimize',
        json={'code': test_code},
        headers={'Content-Type': 'application/json'}
    )

    # Print results
    if response.status_code == 200:
        result = response.json()
        print("\nOriginal Code:")
        print(result['original_code'])
        print("\nOptimized Code:")
        print(result['optimized_code'])
        print("\nChanges Made:")
        for change in result['changes']:
            print(f"- {change}")
        
        print("\nPerformance Metrics:")
        metrics = result['metrics']
        print("\nOriginal Version:")
        print(f"Emissions: {metrics['original']['emissions']:.10f} kg CO2e")
        print(f"Energy: {metrics['original']['energy']:.10f} kWh")
        print(f"Time: {metrics['original']['execution_time']:.2f} seconds")
        
        print("\nOptimized Version:")
        print(f"Emissions: {metrics['optimized']['emissions']:.10f} kg CO2e")
        print(f"Energy: {metrics['optimized']['energy']:.10f} kWh")
        print(f"Time: {metrics['optimized']['execution_time']:.2f} seconds")
        
        print("\nImprovements:")
        improvements = metrics['improvements']
        print(f"Emissions Reduction: {improvements['emissions_reduction']:.10f} kg CO2e")
        print(f"Energy Reduction: {improvements['energy_reduction']:.10f} kWh")
        print(f"Time Reduction: {improvements['time_reduction']:.2f} seconds")
    else:
        print(f"Error: {response.json()['error']}")

if __name__ == "__main__":
    test_optimization() 