from flask import Flask, request, jsonify
from imageToCode import CodeExtractor
import tempfile
import os
from flask_cors import CORS
import pytesseract

from static_analyzer import StaticCodeAnalyzer
from code_reformatter import refactor_code
import ast
import time
import sys
import io
from contextlib import redirect_stdout
import threading
import multiprocessing
from PIL import Image
import base64

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe';

app = Flask(__name__)
CORS(app) 
extractor = CodeExtractor()
analyzer = StaticCodeAnalyzer()

print("CONNECT.PY IS RUNNING")

#----------------------------------------------- IMAGE - TO - TEXT -----------------------------------------------

@app.route('/image-to-code', methods=['POST'])
def image_to_code():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            file.save(tmp.name)
            extracted_code = extractor.extract_code_from_image(tmp.name)
        os.remove(tmp.name)
        if extracted_code is None:
            return jsonify({'error': 'Could not extract code'}), 500
        print("EXTRACTED CODE:", extracted_code)
        return jsonify({'code': extracted_code})
        
    except Exception as e:
        print("ERROR:", e)
        return jsonify({'error': str(e)}), 500

#----------------------------------------------- OPTIMIZE -----------------------------------------------

print("CONNECT.PY IS RUNNING")

@app.route('/optimize', methods=['POST'])
def optimize_code():
    """Endpoint to receive code and return optimized version with static analysis comparison."""
    print("OPTIMIZE ENDPOINT CALLED")
    try:
        data = request.get_json()
        print(data)
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400

        original_code = data['code']
        input_size_n = data.get('input_size_n', 1000000)
        runs_per_year = data.get('runs_per_year', 1000)
        lat = data.get('lat')
        lon = data.get('lon')
        keep_comments = data.get('keep_comments', True)
        keep_fstrings = data.get('keep_fstrings', True)

        # First, try to refactor the code
        refactored_code, changes = refactor_code(original_code, keep_comments=keep_comments, keep_fstrings=keep_fstrings)
        print("Refactored code:", refactored_code)
        print("Changes:", changes)
        
        if not refactored_code:
            return jsonify({
                'error': 'Code refactoring failed',
                'details': changes
            }), 400

        # Analyze both versions using static analysis
        original_analysis = analyzer.analyze_code(
            code=original_code,
            input_size_n=input_size_n,
            runs_per_year=runs_per_year,
            lat=lat,
            lon=lon
        )
        
        optimized_analysis = analyzer.analyze_code(
            code=refactored_code,
            input_size_n=input_size_n,
            runs_per_year=runs_per_year,
            lat=lat,
            lon=lon
        )

        # Check for errors in analysis
        if 'error' in original_analysis or 'error' in optimized_analysis:
            return jsonify({
                'error': 'Error in static analysis',
                'original_error': original_analysis.get('error'),
                'optimized_error': optimized_analysis.get('error')
            }), 500

        # Calculate improvements
        emissions_reduction = original_analysis['emissions_gco2'] - optimized_analysis['emissions_gco2']
        energy_reduction = original_analysis['estimated']['energy_kwh'] - optimized_analysis['estimated']['energy_kwh']
        time_reduction = original_analysis['estimated']['runtime_s'] - optimized_analysis['estimated']['runtime_s']

        return jsonify({
            'original_code': original_code,
            'optimized_code': refactored_code,
            'changes': changes,
            'metrics': {
                'original': {
                    'emissions': original_analysis['emissions_gco2'] / 1000,  # Convert to kg CO2
                    'energy': original_analysis['estimated']['energy_kwh'],
                    'execution_time': original_analysis['estimated']['runtime_s'],
                    'time_complexity': original_analysis['metrics']['time_complexity'],
                    'space_complexity': original_analysis['metrics']['space_complexity'],
                    'cyclomatic_complexity': original_analysis['metrics']['cyclomatic_complexity'],
                    'eco_score': original_analysis['eco_score']
                },
                'optimized': {
                    'emissions': optimized_analysis['emissions_gco2'] / 1000,  # Convert to kg CO2
                    'energy': optimized_analysis['estimated']['energy_kwh'],
                    'execution_time': optimized_analysis['estimated']['runtime_s'],
                    'time_complexity': optimized_analysis['metrics']['time_complexity'],
                    'space_complexity': optimized_analysis['metrics']['space_complexity'],
                    'cyclomatic_complexity': optimized_analysis['metrics']['cyclomatic_complexity'],
                    'eco_score': optimized_analysis['eco_score']
                },
                'improvements': {
                    'emissions_reduction': emissions_reduction / 1000,  # Convert to kg CO2
                    'energy_reduction': energy_reduction,
                    'time_reduction': time_reduction
                }
            },
            'static_analysis': {
                'original': original_analysis,
                'optimized': optimized_analysis
            }
        })

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
