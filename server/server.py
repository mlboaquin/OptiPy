from flask import Flask, request, jsonify
from flask_cors import CORS
from static_analyzer import StaticCodeAnalyzer
import time

app = Flask(__name__)
CORS(app)

# Initialize the static analyzer
analyzer = StaticCodeAnalyzer()

# Legacy functions removed - now using static analysis

@app.route('/analyze', methods=['POST'])
def analyze_code():
    """Static code analysis endpoint for emissions estimation."""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400

        code = data['code']
        input_size_n = data.get('input_size_n', 1000000)
        runs_per_year = data.get('runs_per_year', 1000)
        lat = data.get('lat')
        lon = data.get('lon')

        # Perform static analysis
        result = analyzer.analyze_code(
            code=code,
            input_size_n=input_size_n,
            runs_per_year=runs_per_year,
            lat=lat,
            lon=lon
        )

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

# Legacy endpoint for backward compatibility
@app.route('/measure', methods=['POST'])
def measure_emissions():
    """Legacy endpoint - redirects to static analysis."""
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400

        # Convert to new format and analyze
        result = analyzer.analyze_code(
            code=data['code'],
            input_size_n=1000000,  # Default input size
            runs_per_year=1000,    # Default runs per year
            lat=None,
            lon=None
        )

        if 'error' in result:
            return jsonify(result), 400

        # Simplified response with only emissions and energy
        return jsonify({
            'emissions': result['emissions_gco2'] / 1000,  # Convert to kg CO2
            'energy': result['estimated']['energy_kwh'],
            'static_analysis': {
                'time_complexity': result['metrics']['time_complexity'],
                'space_complexity': result['metrics']['space_complexity'],
                'cyclomatic_complexity': result['metrics']['cyclomatic_complexity'],
                'eco_score': result['eco_score'],
                'suggestions': result['suggestions'],
                'confidence': result['confidence']
            }
        })

    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

 

if __name__ == '__main__':
    # Run Flask server
    app.run(debug=True, port=5000) 