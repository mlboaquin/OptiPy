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

  const formatMetrics = (metrics: any) => {
    if (!metrics) return '';
    
    console.log('Raw metrics data:', metrics); // Debug log
    
    let formattedText = '';
    
    // Helper function to format numbers in scientific notation
    const formatScientific = (value: number) => {
      if (value === 0) return '0';
      const exp = Math.floor(Math.log10(Math.abs(value)));
      const mantissa = value / Math.pow(10, exp);
      return `${mantissa.toFixed(6)} × 10^${exp}`;
    };
    
    // Check if this is the simple structure (emissions, energy, execution_time)
    if (metrics.emissions !== undefined || metrics.energy !== undefined || metrics.execution_time !== undefined) {
      formattedText += '🌱 EMISSIONS DATA\n';
      formattedText += '═══════════════════\n\n';
      
      if (metrics.emissions !== undefined) {
        formattedText += `EMISSION:\n${formatScientific(Number(metrics.emissions))} kg CO2eq\n\n`;
      }
      
      if (metrics.energy !== undefined) {
        formattedText += `ENERGY:\n${formatScientific(Number(metrics.energy))} kWh\n\n`;
      }
      
      if (metrics.execution_time !== undefined) {
        formattedText += `EXECUTION TIME:\n${Number(metrics.execution_time).toFixed(15)} s\n`;
      }
      
      return formattedText;
    }
    
    // Handle different response structures for complex data
    const emissionsData = metrics.emissions || metrics;
    const timingData = metrics.timing || {};
    const hardwareData = metrics.hardware || {};
    
    console.log('Emissions data:', emissionsData); // Debug log
    console.log('Timing data:', timingData); // Debug log
    console.log('Hardware data:', hardwareData); // Debug log
    
    // Check if we have any data at all
    const hasEmissionsData = emissionsData && Object.keys(emissionsData).length > 0;
    const hasTimingData = Object.keys(timingData).length > 0;
    const hasHardwareData = Object.keys(hardwareData).length > 0;
    
    console.log('Has emissions data:', hasEmissionsData); // Debug log
    console.log('Has timing data:', hasTimingData); // Debug log
    console.log('Has hardware data:', hasHardwareData); // Debug log
    
    // Format emissions data
    if (hasEmissionsData) {
      formattedText += '🌱 EMISSIONS DATA\n';
      formattedText += '═══════════════════\n\n';
      
      // Energy data
      if (emissionsData.cpu_energy !== undefined) {
        formattedText += `CPU Energy:     ${Number(emissionsData.cpu_energy).toFixed(4)} kWh\n`;
      }
      if (emissionsData.gpu_energy !== undefined) {
        formattedText += `GPU Energy:     ${Number(emissionsData.gpu_energy).toFixed(4)} kWh\n`;
      }
      if (emissionsData.ram_energy !== undefined) {
        formattedText += `RAM Energy:     ${Number(emissionsData.ram_energy).toFixed(4)} kWh\n`;
      }
      if (emissionsData.total_energy !== undefined) {
        formattedText += `Total Energy:   ${Number(emissionsData.total_energy).toFixed(4)} kWh\n`;
      }
      if (emissionsData.energy !== undefined) {
        formattedText += `Energy:         ${Number(emissionsData.energy).toFixed(4)} kWh\n`;
      }
      
      formattedText += '\n';
      
      // Power data
      if (emissionsData.cpu_power !== undefined) {
        formattedText += `CPU Power:      ${Number(emissionsData.cpu_power).toFixed(2)} W\n`;
      }
      if (emissionsData.gpu_power !== undefined) {
        formattedText += `GPU Power:      ${Number(emissionsData.gpu_power).toFixed(2)} W\n`;
      }
      if (emissionsData.ram_power !== undefined) {
        formattedText += `RAM Power:      ${Number(emissionsData.ram_power).toFixed(2)} W\n`;
      }
      if (emissionsData.total_power !== undefined) {
        formattedText += `Total Power:    ${Number(emissionsData.total_power).toFixed(2)} W\n`;
      }
      if (emissionsData.power !== undefined) {
        formattedText += `Power:          ${Number(emissionsData.power).toFixed(2)} W\n`;
      }
      
      formattedText += '\n';
      
      // Emissions data
      if (emissionsData.cpu_emissions !== undefined) {
        formattedText += `CPU Emissions:  ${Number(emissionsData.cpu_emissions).toFixed(4)} kgCO2\n`;
      }
      if (emissionsData.gpu_emissions !== undefined) {
        formattedText += `GPU Emissions:  ${Number(emissionsData.gpu_emissions).toFixed(4)} kgCO2\n`;
      }
      if (emissionsData.ram_emissions !== undefined) {
        formattedText += `RAM Emissions:  ${Number(emissionsData.ram_emissions).toFixed(4)} kgCO2\n`;
      }
      if (emissionsData.total_emissions !== undefined) {
        formattedText += `Total Emissions: ${Number(emissionsData.total_emissions).toFixed(4)} kgCO2\n`;
      }
      if (emissionsData.emissions !== undefined) {
        formattedText += `Emissions:      ${Number(emissionsData.emissions).toFixed(4)} kgCO2\n`;
      }
    }
    
    // Format timing data
    if (hasTimingData) {
      formattedText += '\n⏱️  TIMING DATA\n';
      formattedText += '═══════════════════\n\n';
      
      if (timingData.duration !== undefined) {
        formattedText += `Duration:       ${Number(timingData.duration).toFixed(4)} seconds\n`;
      }
      if (timingData.start_time !== undefined) {
        formattedText += `Start Time:     ${new Date(timingData.start_time).toLocaleString()}\n`;
      }
      if (timingData.end_time !== undefined) {
        formattedText += `End Time:       ${new Date(timingData.end_time).toLocaleString()}\n`;
      }
    }
    
    // Format hardware data
    if (hasHardwareData) {
      formattedText += '\n💻 HARDWARE INFO\n';
      formattedText += '═══════════════════\n\n';
      
      if (hardwareData.cpu_model) {
        formattedText += `CPU Model:      ${hardwareData.cpu_model}\n`;
      }
      if (hardwareData.gpu_model) {
        formattedText += `GPU Model:      ${hardwareData.gpu_model}\n`;
      }
      if (hardwareData.ram_total) {
        formattedText += `Total RAM:      ${hardwareData.ram_total} GB\n`;
      }
    }
    
    // If no structured data found, show raw data
    if (!hasEmissionsData && !hasTimingData && !hasHardwareData) {
      formattedText = '📊 MEASUREMENT RESULTS\n═══════════════════\n\n';
      formattedText += JSON.stringify(metrics, null, 2);
    }
    
    console.log('Final formatted text:', formattedText); // Debug log
    return formattedText;
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

  const formatHardwareInfo = (hardwareInfo: any) => {
    if (!hardwareInfo) return '';
    
    let formattedText = '';
    
    formattedText += '💻 HARDWARE INFORMATION\n';
    formattedText += '═══════════════════\n\n';
    
    // CPU Information
    formattedText += '🖥️  CPU\n';
    formattedText += '───\n';
    formattedText += `Model:          ${hardwareInfo.cpu.model}\n`;
    formattedText += `Cores:          ${hardwareInfo.cpu.cores}\n`;
    formattedText += `Threads:        ${hardwareInfo.cpu.threads}\n`;
    if (hardwareInfo.cpu.frequency > 0) {
      formattedText += `Frequency:      ${(hardwareInfo.cpu.frequency / 1000).toFixed(2)} GHz\n`;
    }
    formattedText += '\n';
    
    // GPU Information
    formattedText += '🎮 GPU\n';
    formattedText += '───\n';
    formattedText += `Model:          ${hardwareInfo.gpu.model}\n`;
    if (hardwareInfo.gpu.memory > 0) {
      formattedText += `Memory:         ${hardwareInfo.gpu.memory} MB\n`;
    }
    formattedText += '\n';
    
    // Memory Information
    formattedText += '🧠 MEMORY\n';
    formattedText += '───\n';
    formattedText += `Total:          ${hardwareInfo.memory.total.toFixed(1)} GB\n`;
    formattedText += `Available:      ${hardwareInfo.memory.available.toFixed(1)} GB\n`;
    formattedText += `Usage:          ${hardwareInfo.memory.percent.toFixed(1)}%\n`;
    formattedText += '\n';
    
    // System Information
    formattedText += '🖥️  SYSTEM\n';
    formattedText += '───\n';
    formattedText += `Platform:       ${hardwareInfo.platform}\n`;
    formattedText += `Python:         ${hardwareInfo.python_version}\n`;
    
    return formattedText;
  };

  return (
    <div className={styles.container}>
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
              <textarea
                readOnly
                value={result ? formatMetrics(result.metrics) : ''}
                placeholder="Your emissions measurement results will appear here"
                className={styles.textarea}
              />
              <div className={styles.deleteIcon} onClick={() => navigator.clipboard.writeText(result ? formatMetrics(result.metrics) : '')}>
                <svg width="22" height="26" viewBox="0 0 27 34" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M7.6665 5.02789V23.1952C7.6665 23.9983 7.9738 24.7684 8.52078 25.3363C9.06776 25.9041 9.80962 26.2231 10.5832 26.2231H22.2498C23.0234 26.2231 23.7653 25.9041 24.3122 25.3363C24.8592 24.7684 25.1665 23.9983 25.1665 23.1952V9.9361C25.1665 9.53272 25.0888 9.13342 24.938 8.76165C24.7873 8.38987 24.5665 8.05312 24.2886 7.77116L19.4542 2.86295C18.9093 2.30984 18.1775 2.0001 17.4155 2H10.5832C9.80962 2 9.06776 2.31901 8.52078 2.88685C7.9738 3.45469 7.6665 4.22484 7.6665 5.02789Z" stroke="#3a7f0d" strokeOpacity="0.96" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M19.3333 26.223V29.2509C19.3333 30.0539 19.026 30.8241 18.479 31.3919C17.932 31.9597 17.1901 32.2787 16.4166 32.2787H4.74992C3.97637 32.2787 3.2345 31.9597 2.68752 31.3919C2.14054 30.8241 1.83325 30.0539 1.83325 29.2509V12.5975C1.83325 11.7944 2.14054 11.0243 2.68752 10.4564C3.2345 9.88859 3.97637 9.56958 4.74992 9.56958H7.66659" stroke="#3a7f0d" strokeOpacity="0.96" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
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

      {/* Calculations Section */}
      {result && (
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
              {showCalculations ? 'Hide Calculations' : 'Show Detailed Calculations'}
            </button>
          </div>

          {showCalculations && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '2rem',
              marginTop: '1rem'
            }}>
              {/* Hardware Information */}
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
                overflowY: 'auto'
              }}>
                {result.hardware_info ? formatHardwareInfo(result.hardware_info) : 'Hardware information not available'}
              </div>

              {/* Detailed Calculations */}
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
                overflowY: 'auto'
              }}>
                {result.calculations ? formatCalculations(result.calculations) : 'Calculation details not available'}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
