from flask import Flask, request, jsonify
from flask_cors import CORS
from codecarbon import EmissionsTracker
from code_reformatter import refactor_code
import ast
import time
import sys
import io
from contextlib import redirect_stdout
import threading
import multiprocessing

app = Flask(__name__)
CORS(app)

class EmissionsRunner(multiprocessing.Process):
    """Class to run code and track emissions in a separate process."""
    def __init__(self, code_str):
        super().__init__()
        self.code_str = code_str
        self.result = multiprocessing.Manager().dict()

    def run(self):
        try:
            # Create and execute function
            namespace = {}
            exec(self.code_str, globals(), namespace)
            func = namespace['process_data']  # The function must be named process_data

            # Track emissions
            tracker = EmissionsTracker(log_level="error", save_to_file=False)
            tracker.start()
            start_time = time.time()
            
            # Capture output and run function
            with redirect_stdout(io.StringIO()):
                func()
                
            end_time = time.time()
            emissions = tracker.stop()
            energy = tracker.final_emissions_data.energy_consumed
            execution_time = end_time - start_time
            
            self.result.update({
                'emissions': emissions,
                'energy': energy,
                'execution_time': execution_time
            })
        except Exception as e:
            self.result.update({'error': str(e)})

def run_with_emissions_tracking(code_str: str) -> dict:
    """Run code in a separate process and track emissions."""
    runner = EmissionsRunner(code_str)
    runner.start()
    runner.join()
    
    if 'error' in runner.result:
        return {'error': runner.result['error']}
    return dict(runner.result)

def create_wrapped_code(code_str: str) -> str:
    """Wrap code in a function named process_data."""
    # Remove any existing process_data function definition
    lines = code_str.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('def process_data')]
    
    # Create the wrapped code
    wrapped_code = "def process_data():\n"
    wrapped_code += "\n".join(f"    {line}" for line in filtered_lines if line.strip())
    return wrapped_code

@app.route('/optimize', methods=['POST'])
def optimize_code():
    """Endpoint to receive code and return optimized version with emissions comparison."""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400

        original_code = data['code']

        # First, try to refactor the code
        refactored_code, changes = refactor_code(original_code)
        
        if not refactored_code:
            return jsonify({
                'error': 'Code refactoring failed',
                'details': changes
            }), 400

        # Wrap both versions in process_data function
        wrapped_original = create_wrapped_code(original_code)
        wrapped_optimized = create_wrapped_code(refactored_code)

        # Measure emissions for both versions using multiprocessing
        original_metrics = run_with_emissions_tracking(wrapped_original)
        optimized_metrics = run_with_emissions_tracking(wrapped_optimized)

        # Check for errors in measurements
        if 'error' in original_metrics or 'error' in optimized_metrics:
            return jsonify({
                'error': 'Error measuring emissions',
                'original_error': original_metrics.get('error'),
                'optimized_error': optimized_metrics.get('error')
            }), 500

        # Calculate improvements
        emissions_reduction = original_metrics['emissions'] - optimized_metrics['emissions']
        energy_reduction = original_metrics['energy'] - optimized_metrics['energy']
        time_reduction = original_metrics['execution_time'] - optimized_metrics['execution_time']

        return jsonify({
            'original_code': original_code,
            'optimized_code': refactored_code,
            'changes': changes,
            'metrics': {
                'original': original_metrics,
                'optimized': optimized_metrics,
                'improvements': {
                    'emissions_reduction': emissions_reduction,
                    'energy_reduction': energy_reduction,
                    'time_reduction': time_reduction
                }
            }
        })

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Run Flask with threading disabled to avoid conflicts with multiprocessing
    app.run(debug=True, port=5000, threaded=False) 