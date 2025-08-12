from flask import Flask, request, jsonify
from flask_cors import CORS
from codecarbon import EmissionsTracker
from code_reformatter import refactor_code
import ast
import time
import sys
import io
import math
from contextlib import redirect_stdout
import threading
import multiprocessing
from PIL import Image
import pytesseract
import base64
import psutil
import platform

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
            
            # Get detailed emissions data
            emissions_data = tracker.final_emissions_data
            
            self.result.update({
                'emissions': emissions,
                'energy': energy,
                'execution_time': execution_time,
                'detailed_data': {
                    'cpu_energy': getattr(emissions_data, 'cpu_energy', 0),
                    'gpu_energy': getattr(emissions_data, 'gpu_energy', 0),
                    'ram_energy': getattr(emissions_data, 'ram_energy', 0),
                    'total_energy': energy,
                    'cpu_power': getattr(emissions_data, 'cpu_power', 0),
                    'gpu_power': getattr(emissions_data, 'gpu_power', 0),
                    'ram_power': getattr(emissions_data, 'ram_power', 0),
                    'total_power': getattr(emissions_data, 'total_power', 0),
                    'cpu_emissions': getattr(emissions_data, 'cpu_emissions', 0),
                    'gpu_emissions': getattr(emissions_data, 'gpu_emissions', 0),
                    'ram_emissions': getattr(emissions_data, 'ram_emissions', 0),
                    'total_emissions': emissions
                }
            })
        except Exception as e:
            self.result.update({'error': str(e)})

def get_hardware_info():
    """Get detailed hardware information for calculations."""
    try:
        cpu_info = {
            'model': platform.processor() or 'Unknown CPU',
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True),
            'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
        
        memory_info = {
            'total': psutil.virtual_memory().total / (1024**3),  # GB
            'available': psutil.virtual_memory().available / (1024**3),  # GB
            'percent': psutil.virtual_memory().percent
        }
        
        # Try to get GPU info (this might not work on all systems)
        gpu_info = {
            'model': 'Unknown GPU',
            'memory': 0
        }
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_info = {
                    'model': gpus[0].name,
                    'memory': gpus[0].memoryTotal
                }
        except:
            pass
        
        return {
            'cpu': cpu_info,
            'gpu': gpu_info,
            'memory': memory_info,
            'platform': platform.system(),
            'python_version': platform.python_version()
        }
    except Exception as e:
        return {
            'cpu': {'model': 'Unknown', 'cores': 0, 'threads': 0, 'frequency': 0},
            'gpu': {'model': 'Unknown', 'memory': 0},
            'memory': {'total': 0, 'available': 0, 'percent': 0},
            'platform': 'Unknown',
            'python_version': 'Unknown',
            'error': str(e)
        }

def calculate_emissions_breakdown(detailed_data, execution_time, hardware_info):
    """Calculate detailed emissions breakdown with explanations."""
    
    def format_scientific(value):
        """Format number in scientific notation."""
        if value == 0:
            return '0'
        exp = int(math.floor(math.log10(abs(value))))
        mantissa = value / (10 ** exp)
        return f"{mantissa:.6f} × 10^{exp}"
    
    calculations = {
        'energy_calculation': {
            'formula': 'Energy (kWh) = Power (W) × Time (hours)',
            'steps': []
        },
        'emissions_calculation': {
            'formula': 'Emissions (kg CO2) = Energy (kWh) × Carbon Intensity (kg CO2/kWh)',
            'steps': []
        },
        'power_breakdown': {
            'cpu': detailed_data.get('cpu_power', 0),
            'gpu': detailed_data.get('gpu_power', 0),
            'ram': detailed_data.get('ram_power', 0),
            'total': detailed_data.get('total_power', 0)
        },
        'energy_breakdown': {
            'cpu': detailed_data.get('cpu_energy', 0),
            'gpu': detailed_data.get('gpu_energy', 0),
            'ram': detailed_data.get('ram_energy', 0),
            'total': detailed_data.get('total_energy', 0)
        },
        'emissions_breakdown': {
            'cpu': detailed_data.get('cpu_emissions', 0),
            'gpu': detailed_data.get('gpu_emissions', 0),
            'ram': detailed_data.get('ram_emissions', 0),
            'total': detailed_data.get('total_emissions', 0)
        }
    }
    
    # Add calculation steps
    if execution_time > 0:
        time_hours = execution_time / 3600
        calculations['energy_calculation']['steps'].append(
            f"Execution time: {execution_time:.15f} seconds = {format_scientific(time_hours)} hours"
        )
        
        if calculations['power_breakdown']['cpu'] > 0:
            cpu_energy_calc = calculations['power_breakdown']['cpu'] * time_hours
            calculations['energy_calculation']['steps'].append(
                f"CPU Energy = {format_scientific(calculations['power_breakdown']['cpu'])}W × {format_scientific(time_hours)}h = {format_scientific(cpu_energy_calc)} kWh"
            )
        
        if calculations['power_breakdown']['gpu'] > 0:
            gpu_energy_calc = calculations['power_breakdown']['gpu'] * time_hours
            calculations['energy_calculation']['steps'].append(
                f"GPU Energy = {format_scientific(calculations['power_breakdown']['gpu'])}W × {format_scientific(time_hours)}h = {format_scientific(gpu_energy_calc)} kWh"
            )
        
        if calculations['power_breakdown']['ram'] > 0:
            ram_energy_calc = calculations['power_breakdown']['ram'] * time_hours
            calculations['energy_calculation']['steps'].append(
                f"RAM Energy = {format_scientific(calculations['power_breakdown']['ram'])}W × {format_scientific(time_hours)}h = {format_scientific(ram_energy_calc)} kWh"
            )
    
    # Add emissions calculation steps (assuming average carbon intensity)
    carbon_intensity = 0.5  # kg CO2/kWh (global average, varies by region)
    calculations['emissions_calculation']['carbon_intensity'] = carbon_intensity
    calculations['emissions_calculation']['steps'].append(
        f"Using carbon intensity: {carbon_intensity} kg CO2/kWh (global average)"
    )
    
    if calculations['energy_breakdown']['total'] > 0:
        total_emissions_calc = calculations['energy_breakdown']['total'] * carbon_intensity
        calculations['emissions_calculation']['steps'].append(
            f"Total Emissions = {format_scientific(calculations['energy_breakdown']['total'])} kWh × {carbon_intensity} kg CO2/kWh = {format_scientific(total_emissions_calc)} kg CO2"
        )
    
    return calculations

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
        print(data)
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

@app.route('/measure', methods=['POST'])
def measure_emissions():
    """Endpoint to receive code and return detailed emissions measurements with calculations."""
    try:
        data = request.get_json()
        print(data)
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400

        code = data['code']

        # Wrap code in process_data function
        wrapped_code = create_wrapped_code(code)

        # Measure emissions using multiprocessing
        metrics = run_with_emissions_tracking(wrapped_code)

        # Check for errors in measurements
        if 'error' in metrics:
            return jsonify({
                'error': 'Error measuring emissions',
                'details': metrics['error']
            }), 500

        # Get hardware information
        hardware_info = get_hardware_info()
        
        # Calculate detailed breakdown
        detailed_data = metrics.get('detailed_data', {})
        calculations = calculate_emissions_breakdown(
            detailed_data, 
            metrics['execution_time'], 
            hardware_info
        )

        return jsonify({
            'metrics': {
                'emissions': metrics['emissions'],
                'energy': metrics['energy'],
                'execution_time': metrics['execution_time'],
                'detailed_data': detailed_data
            },
            'hardware_info': hardware_info,
            'calculations': calculations,
            'timing': {
                'duration': metrics['execution_time'],
                'start_time': time.time() - metrics['execution_time'],
                'end_time': time.time()
            }
        })

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({'status': 'healthy'})

@app.route('/image-to-code', methods=['POST'])
def image_to_code():
    """Endpoint to receive code as an image and return extracted code."""
    try:
        print(request.content_type)  # Log the content type
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file provided'}), 400

        # Decode base64 image
        try:
            image = Image.open(file.stream)  # Use the file stream directly
        except Exception as e:
            return jsonify({'error': f'Invalid image format: {str(e)}'}), 400

        # Extract text from image using OCR
        try:
            extracted_code = pytesseract.image_to_string(image)
            if not extracted_code.strip():
                return jsonify({'error': 'No text could be extracted from the image'}), 400
        except Exception as e:
            return jsonify({'error': f'OCR failed: {str(e)}'}), 500

        return jsonify({
            'code': extracted_code
        })

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    # Run Flask with threading disabled to avoid conflicts with multiprocessing
    app.run(debug=True, port=5000, threaded=False) 