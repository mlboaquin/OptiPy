import React, { useState, useEffect } from 'react';
import { Textarea, Button, Text, Card, Title, Divider } from '@mantine/core';
import styles from './CodeCalculator.module.css';
import axios from 'axios';

export default function CodeCalculator() {
  const [code, setCode] = useState('');
  const [status, setStatus] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showCalculations, setShowCalculations] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (loading) {
      let dots = 0;
      interval = setInterval(() => {
        setStatus(`Measuring emissions${'.'.repeat(dots % 5)}`);
        dots++;
      }, 500);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handlePaste = () => {
    navigator.clipboard.readText().then(text => setCode(text));
  };

  const handleDelete = () => {
    setCode('');
    setStatus('');
    setResult(null);
    setShowCalculations(false);
  };

  const handleMeasure = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/measure', {
        code: code
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      setStatus('Emissions measured successfully');
      console.log('Full response:', response.data); // Debug log
      setResult(response.data);
    } catch (error) {
      setStatus('Error measuring emissions');
      console.error(error);
      
      // For testing purposes, let's add some sample data when there's an error
      console.log('Adding sample data for testing...');
      const sampleData = {
        metrics: {
          emissions: 0.0007,
          energy: 0.0023,
          execution_time: 1.2345,
          detailed_data: {
            cpu_energy: 0.0012,
            gpu_energy: 0.0008,
            ram_energy: 0.0003,
            total_energy: 0.0023,
            cpu_power: 45.2,
            gpu_power: 12.8,
            ram_power: 8.5,
            total_power: 66.5,
            cpu_emissions: 0.0004,
            gpu_emissions: 0.0002,
            ram_emissions: 0.0001,
            total_emissions: 0.0007
          }
        },
        hardware_info: {
          cpu: {
            model: "Intel Core i7-10700K",
            cores: 8,
            threads: 16,
            frequency: 3600
          },
          gpu: {
            model: "NVIDIA RTX 3070",
            memory: 8192
          },
          memory: {
            total: 16,
            available: 12.5,
            percent: 22.5
          },
          platform: "Windows",
          python_version: "3.9.0"
        },
                 calculations: {
           energy_calculation: {
             formula: 'Energy (kWh) = Power (W) × Time (hours)',
             steps: [
               'Execution time: 1.234500000000000 seconds = 3.430556 × 10^-4 hours',
               'CPU Energy = 4.520000 × 10^1W × 3.430556 × 10^-4h = 1.200000 × 10^-3 kWh',
               'GPU Energy = 1.280000 × 10^1W × 3.430556 × 10^-4h = 8.000000 × 10^-4 kWh',
               'RAM Energy = 8.500000 × 10^0W × 3.430556 × 10^-4h = 3.000000 × 10^-4 kWh'
             ]
           },
           emissions_calculation: {
             formula: 'Emissions (kg CO2) = Energy (kWh) × Carbon Intensity (kg CO2/kWh)',
             carbon_intensity: 0.5,
             steps: [
               'Using carbon intensity: 0.5 kg CO2/kWh (global average)',
               'Total Emissions = 2.300000 × 10^-3 kWh × 0.5 kg CO2/kWh = 1.150000 × 10^-3 kg CO2'
             ]
           },
          power_breakdown: {
            cpu: 45.2,
            gpu: 12.8,
            ram: 8.5,
            total: 66.5
          },
          energy_breakdown: {
            cpu: 0.0012,
            gpu: 0.0008,
            ram: 0.0003,
            total: 0.0023
          },
          emissions_breakdown: {
            cpu: 0.0004,
            gpu: 0.0002,
            ram: 0.0001,
            total: 0.0007
          }
        },
        timing: {
          duration: 1.2345,
          start_time: Date.now() - 1234,
          end_time: Date.now()
        }
      };
      setResult(sampleData);
    } finally {
      setLoading(false);
    }
  };

  const formatMetrics = (result: any) => {
    if (!result) return { emissions: 0, energy: 0 };
    
    console.log('Raw result data:', result); // Debug log
    
    // Extract emissions and energy from the simplified response
    const emissions = result.emissions || 0;
    const energy = result.energy || 0;
    
    return { emissions, energy };
  };

  const formatCalculations = (calculations: any) => {
    if (!calculations) return '';
    
    // Helper function to format numbers in scientific notation
    const formatScientific = (value: number) => {
      if (value === 0) return '0';
      const exp = Math.floor(Math.log10(Math.abs(value)));
      const mantissa = value / Math.pow(10, exp);
      return `${mantissa.toFixed(6)} × 10^${exp}`;
    };
    
    let formattedText = '';
    
    // Energy Calculation Section
    formattedText += '⚡ ENERGY CALCULATION\n';
    formattedText += '═══════════════════\n\n';
    formattedText += `Formula: ${calculations.energy_calculation.formula}\n\n`;
    
    calculations.energy_calculation.steps.forEach((step: string, index: number) => {
      formattedText += `${index + 1}. ${step}\n`;
    });
    
    formattedText += '\n';
    
    // Power Breakdown
    formattedText += '🔌 POWER BREAKDOWN\n';
    formattedText += '═══════════════════\n\n';
    formattedText += `CPU Power:      ${formatScientific(calculations.power_breakdown.cpu)} W\n`;
    formattedText += `GPU Power:      ${formatScientific(calculations.power_breakdown.gpu)} W\n`;
    formattedText += `RAM Power:      ${formatScientific(calculations.power_breakdown.ram)} W\n`;
    formattedText += `Total Power:    ${formatScientific(calculations.power_breakdown.total)} W\n\n`;
    
    // Energy Breakdown
    formattedText += '⚡ ENERGY BREAKDOWN\n';
    formattedText += '═══════════════════\n\n';
    formattedText += `CPU Energy:     ${formatScientific(calculations.energy_breakdown.cpu)} kWh\n`;
    formattedText += `GPU Energy:     ${formatScientific(calculations.energy_breakdown.gpu)} kWh\n`;
    formattedText += `RAM Energy:     ${formatScientific(calculations.energy_breakdown.ram)} kWh\n`;
    formattedText += `Total Energy:   ${formatScientific(calculations.energy_breakdown.total)} kWh\n\n`;
    
    // Emissions Calculation Section
    formattedText += '🌱 EMISSIONS CALCULATION\n';
    formattedText += '═══════════════════\n\n';
    formattedText += `Formula: ${calculations.emissions_calculation.formula}\n\n`;
    
    calculations.emissions_calculation.steps.forEach((step: string, index: number) => {
      formattedText += `${index + 1}. ${step}\n`;
    });
    
    formattedText += '\n';
    
    // Emissions Breakdown
    formattedText += '🌱 EMISSIONS BREAKDOWN\n';
    formattedText += '═══════════════════\n\n';
    formattedText += `CPU Emissions:  ${formatScientific(calculations.emissions_breakdown.cpu)} kg CO2\n`;
    formattedText += `GPU Emissions:  ${formatScientific(calculations.emissions_breakdown.gpu)} kg CO2\n`;
    formattedText += `RAM Emissions:  ${formatScientific(calculations.emissions_breakdown.ram)} kg CO2\n`;
    formattedText += `Total Emissions: ${formatScientific(calculations.emissions_breakdown.total)} kg CO2\n`;
    
    return formattedText;
  };

  const formatStaticAnalysis = (staticAnalysis: any) => {
    if (!staticAnalysis) return '';
    
    let formattedText = '';
    
    formattedText += '🔍 STATIC CODE ANALYSIS\n';
    formattedText += '═══════════════════\n\n';
    
    // Complexity Information
    formattedText += '📊 COMPLEXITY METRICS\n';
    formattedText += '───\n';
    formattedText += `Time Complexity:     ${staticAnalysis.time_complexity}\n`;
    formattedText += `Space Complexity:    ${staticAnalysis.space_complexity}\n`;
    formattedText += `Cyclomatic Complexity: ${staticAnalysis.cyclomatic_complexity}\n`;
    formattedText += `Eco Score:           ${staticAnalysis.eco_score.toFixed(1)}/100\n`;
    formattedText += `Confidence:          ${(staticAnalysis.confidence * 100).toFixed(1)}%\n\n`;
    
    // Complexity Explanations
    formattedText += '📚 COMPLEXITY EXPLANATIONS\n';
    formattedText += '───\n';
    formattedText += `Time Complexity (${staticAnalysis.time_complexity}):\n`;
    formattedText += `  How execution time grows with input size.\n`;
    formattedText += `  O(1) = constant, O(N) = linear, O(N²) = quadratic\n\n`;
    
    formattedText += `Space Complexity (${staticAnalysis.space_complexity}):\n`;
    formattedText += `  How memory usage grows with input size.\n`;
    formattedText += `  O(1) = constant memory, O(N) = linear memory\n\n`;
    
    formattedText += `Cyclomatic Complexity (${staticAnalysis.cyclomatic_complexity}):\n`;
    formattedText += `  Number of decision paths in code.\n`;
    formattedText += `  Lower = simpler, Higher = more complex\n\n`;
    
    formattedText += `Eco Score (${staticAnalysis.eco_score.toFixed(1)}/100):\n`;
    formattedText += `  Energy efficiency rating.\n`;
    formattedText += `  100 = very efficient, 0 = inefficient\n\n`;
    
    formattedText += `Confidence (${(staticAnalysis.confidence * 100).toFixed(1)}%):\n`;
    formattedText += `  Analysis reliability.\n`;
    formattedText += `  Higher = more accurate estimate\n\n`;
    
    // Suggestions
    if (staticAnalysis.suggestions && staticAnalysis.suggestions.length > 0) {
      formattedText += '💡 OPTIMIZATION SUGGESTIONS\n';
      formattedText += '───\n';
      staticAnalysis.suggestions.forEach((suggestion: string, index: number) => {
        formattedText += `${index + 1}. ${suggestion}\n`;
      });
    }
    
    return formattedText;
  };

  const formatMeasurementExplanations = (result: any) => {
    if (!result) return '';
    
    const emissions = result.emissions || 0;
    const energy = result.energy || 0;
    
    let formattedText = '';
    
    formattedText += '📊 MEASUREMENT EXPLANATIONS\n';
    formattedText += '═══════════════════\n\n';
    
    // Carbon Emissions Section
    formattedText += '🌱 CARBON EMISSIONS\n';
    formattedText += '───\n';
    formattedText += `Your Code Produced: ${emissions.toFixed(6)} kg CO₂\n\n`;
    
    formattedText += 'What this means:\n';
    formattedText += `• Equivalent to driving ${(emissions * 1000 / 120).toFixed(2)} meters by car\n`;
    formattedText += `• Equal to ${(emissions * 1000 / 22).toFixed(2)} trees absorbing CO₂ for a day\n`;
    formattedText += `• Same as sending ${(emissions * 1000 / 4).toFixed(0)} emails\n`;
    formattedText += `• ${emissions < 0.001 ? 'Very low' : emissions < 0.01 ? 'Low' : emissions < 0.1 ? 'Moderate' : 'High'} environmental impact\n\n`;
    
    // Energy Consumption Section
    formattedText += '⚡ ENERGY CONSUMPTION\n';
    formattedText += '───\n';
    formattedText += `Your Code Used: ${energy.toFixed(6)} kWh\n\n`;
    
    formattedText += 'What this means:\n';
    formattedText += `• Powers a 60W light bulb for ${(energy * 1000 / 60).toFixed(1)} hours\n`;
    formattedText += `• Charges a smartphone ${(energy * 1000 / 0.01).toFixed(0)} times\n`;
    formattedText += `• Runs a laptop for ${(energy * 1000 / 50).toFixed(1)} hours\n`;
    formattedText += `• ${energy < 0.001 ? 'Very efficient' : energy < 0.01 ? 'Efficient' : energy < 0.1 ? 'Moderate' : 'Energy intensive'} code\n\n`;
    
    // Environmental Impact
    formattedText += '🌍 ENVIRONMENTAL IMPACT\n';
    formattedText += '───\n';
    const impactLevel = emissions < 0.001 ? 'Minimal' : 
                       emissions < 0.01 ? 'Low' : 
                       emissions < 0.1 ? 'Moderate' : 'Significant';
    
    formattedText += `Overall Impact: ${impactLevel}\n\n`;
    
    if (emissions < 0.001) {
      formattedText += '✅ Your code is very environmentally friendly!\n';
      formattedText += '   Minimal carbon footprint and energy usage.\n\n';
    } else if (emissions < 0.01) {
      formattedText += '✅ Good environmental performance.\n';
      formattedText += '   Low impact with room for minor optimizations.\n\n';
    } else if (emissions < 0.1) {
      formattedText += '⚠️  Moderate environmental impact.\n';
      formattedText += '   Consider optimizing for better efficiency.\n\n';
    } else {
      formattedText += '⚠️  High environmental impact.\n';
      formattedText += '   Significant optimization opportunities exist.\n\n';
    }
    
    // Optimization Tips
    formattedText += '💡 QUICK OPTIMIZATION TIPS\n';
    formattedText += '───\n';
    formattedText += '• Use efficient algorithms (lower time complexity)\n';
    formattedText += '• Minimize memory usage (lower space complexity)\n';
    formattedText += '• Avoid unnecessary loops and calculations\n';
    formattedText += '• Use built-in functions when possible\n';
    formattedText += '• Consider caching for repeated operations\n';
    
    return formattedText;
  };

  return (
    <div className={styles.container} style={{ marginTop: '2rem', marginBottom: '2rem' }}>
      <div className={styles.titleBlock}>
        <img src="/logo.svg" width="100px" alt="Logo" />
        <h2>OptiPy</h2>
      </div>

      <div style={{ 
        textAlign: 'center', 
        marginBottom: '1rem', 
        padding: '0.75rem', 
        backgroundColor: 'rgba(255, 193, 7, 0.1)', 
        border: '1px solid rgba(255, 193, 7, 0.3)', 
        borderRadius: '8px',
        maxWidth: '800px',
        marginLeft: 'auto',
        marginRight: 'auto'
      }}>
        <p style={{ 
          margin: '0', 
          fontSize: '14px', 
          color: '#856404', 
          fontFamily: 'Poppins',
          fontWeight: '400'
        }}>
          <strong>⚠️ Disclaimer:</strong> This tool is designed to work exclusively with Python code. 
          Code that requires external modules, dependencies, or file attachments may not function properly 
          and could result in measurement errors.
        </p>
      </div>

      <div className={styles.squarebox}>
        <div className={styles.sbcontainer}>
          <div className={styles.sbcontainer2}>
            <div className={styles.input}>
              <textarea
                value={code}
                onChange={(event) => setCode(event.currentTarget.value)}
                placeholder="Start by writing or pasting (CTRL + V) your Python code.&#10;&#10;To measure emissions, press (CTRL + Enter)."
                className={styles.textarea}
              />
              <div className={styles.buttonGroup}>
                <button className={styles.pasteBtn} onClick={handlePaste}>Paste Code</button>
              </div>
              <div className={styles.deleteIcon} onClick={handleDelete}>
                <svg width="22" height="26" viewBox="0 0 27 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path id="Vector" d="M1.83325 8.2288H25.1666M10.5833 14.4576V23.8008M16.4166 14.4576V23.8008M3.29159 8.2288L4.74992 26.9152C4.74992 27.7412 5.05721 28.5334 5.60419 29.1174C6.15117 29.7015 6.89304 30.0296 7.66659 30.0296H19.3333C20.1068 30.0296 20.8487 29.7015 21.3956 29.1174C21.9426 28.5334 22.2499 27.7412 22.2499 26.9152L23.7083 8.2288M9.12492 8.2288V3.5572C9.12492 3.14421 9.27856 2.74812 9.55206 2.45609C9.82555 2.16406 10.1965 2 10.5833 2H16.4166C16.8034 2 17.1743 2.16406 17.4478 2.45609C17.7213 2.74812 17.8749 3.14421 17.8749 3.5572V8.2288" stroke="#3a7f0d" strokeOpacity="0.96" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>

            <div className={styles.output}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
                padding: '20px',
                textAlign: 'center'
              }}>
                {result ? (
                  <>
                    <div style={{
                      fontSize: '24px',
                      fontWeight: '600',
                      color: '#2c3e50',
                      marginBottom: '20px',
                      fontFamily: 'Poppins'
                    }}>
                      Carbon Emission: {formatMetrics(result).emissions.toFixed(6)} kg CO₂
                    </div>
                    <div style={{
                      fontSize: '20px',
                      fontWeight: '500',
                      color: '#34495e',
                      fontFamily: 'Poppins'
                    }}>
                      Energy Consumption: {formatMetrics(result).energy.toFixed(6)} kWh
                    </div>
                  </>
                ) : (
                  <div style={{
                    fontSize: '18px',
                    color: '#7f8c8d',
                    fontFamily: 'Poppins'
                  }}>
                    Your emissions measurement results will appear here
                  </div>
                )}
              </div>
            </div>
          </div>

          <button className={styles.btn2} onClick={handleMeasure} disabled={loading}>
            <svg height="24" width="24" fill="#FFFFFF" viewBox="0 0 24 24" data-name="Layer 1" id="Layer_1" className={styles.sparkle}>
              <path d="M10,21.236,6.755,14.745.264,11.5,6.755,8.255,10,1.764l3.245,6.491L19.736,11.5l-6.491,3.245ZM18,21l1.5,3L21,21l3-1.5L21,18l-1.5-3L18,18l-3,1.5ZM19.333,4.667,20.5,7l1.167-2.333L24,3.5,21.667,2.333,20.5,0,19.333,2.333,17,3.5Z"></path>
            </svg>
            <span className={styles.text1}>{loading ? 'Measuring...' : 'Measure Emissions'}</span>
          </button>
        </div>
      </div>

      {/* Static Analysis Section */}
      {result && result.static_analysis && (
        <div style={{ 
          marginTop: '2rem',
          maxWidth: '1200px',
          marginLeft: 'auto',
          marginRight: 'auto'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '1rem'
          }}>
            <button
              onClick={() => setShowCalculations(!showCalculations)}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: showCalculations ? '#e74c3c' : '#27ae60',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                fontFamily: 'Poppins',
                transition: 'background-color 0.3s ease'
              }}
            >
              {showCalculations ? 'Hide Analysis Details' : 'Show Analysis Details'}
            </button>
          </div>

          {showCalculations && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '2rem',
              marginTop: '1rem',
              maxWidth: '1200px',
              width: '100%',
              marginLeft: 'auto',
              marginRight: 'auto'
            }}>
              {/* Static Analysis Details */}
              <div style={{
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '12px',
                padding: '1.5rem',
                fontFamily: 'monospace',
                fontSize: '12px',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
                maxHeight: '500px',
                overflowY: 'auto',
                boxSizing: 'border-box'
              }}>
                {formatStaticAnalysis(result.static_analysis)}
              </div>

              {/* Measurement Explanations */}
              <div style={{
                backgroundColor: '#f8f9fa',
                border: '1px solid #dee2e6',
                borderRadius: '12px',
                padding: '1.5rem',
                fontFamily: 'monospace',
                fontSize: '12px',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
                maxHeight: '500px',
                overflowY: 'auto',
                boxSizing: 'border-box'
              }}>
                {formatMeasurementExplanations(result)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
