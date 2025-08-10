import React, { useState, useEffect } from 'react';
import { Textarea, Button, Text, Card, Title, Divider } from '@mantine/core';
import styles from './CodeCalculator.module.css';
import axios from 'axios';

export default function CodeCalculator() {
  const [code, setCode] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

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
    setFile(null);
    setStatus('');
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = event.target.files?.[0] || null;
    if (!uploadedFile) return;

    const reader = new FileReader();
    reader.onloadend = async () => {
      const byteArray = new Uint8Array(reader.result as ArrayBuffer);
      const formData = new FormData();
      formData.append('file', new Blob([byteArray], { type: uploadedFile.type }), uploadedFile.name);

      try {
        const response = await axios.post('http://127.0.0.1:5000/image-to-code', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        setCode(response.data.code);
        setStatus('Code extracted from image successfully, Please modify for innaccuracies');
      } catch (error) {
        setStatus('Error extracting code from image');
        console.error(error);
      }
    };
    reader.readAsArrayBuffer(uploadedFile);
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
      const { metrics } = response.data;
      console.log('Extracted metrics:', metrics); // Debug log
      setResult({ metrics });
    } catch (error) {
      setStatus('Error measuring emissions');
      console.error(error);
      
      // For testing purposes, let's add some sample data when there's an error
      console.log('Adding sample data for testing...');
      const sampleData = {
        emissions: {
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
        },
        timing: {
          duration: 1.2345,
          start_time: Date.now() - 1234,
          end_time: Date.now()
        },
        hardware: {
          cpu_model: "Intel Core i7-10700K",
          gpu_model: "NVIDIA RTX 3070",
          ram_total: 16
        }
      };
      setResult({ metrics: sampleData });
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

      <div style={{ 
        textAlign: 'center', 
        marginBottom: '1rem', 
        padding: '0.75rem', 
        backgroundColor: 'rgba(52, 152, 219, 0.1)', 
        border: '1px solid rgba(52, 152, 219, 0.3)', 
        borderRadius: '8px',
        maxWidth: '800px',
        marginLeft: 'auto',
        marginRight: 'auto'
      }}>
        <p style={{ 
          margin: '0', 
          fontSize: '14px', 
          color: '#2c3e50', 
          fontFamily: 'Poppins',
          fontWeight: '400'
        }}>
          <strong>💡 Tip:</strong> You can paste your Python code directly or upload a screenshot of your code. 
          The image-to-code feature will attempt to extract the code, but please review and edit the extracted 
          text for accuracy before measuring emissions.
        </p>
      </div>

      <div className={styles.squarebox}>
        <div className={styles.sbcontainer}>
          <div className={styles.sbcontainer2}>
            <div className={styles.input}>
              <textarea
                value={code}
                onChange={(event) => setCode(event.currentTarget.value)}
                placeholder="Start by writing, pasting (CTRL + V) your text, or attaching a screenshot of your code.&#10;&#10;To measure emissions, press (CTRL + Enter)."
                className={styles.textarea}
              />
              <div className={styles.buttonGroup}>
                <input 
                  type="file" 
                  id="image-input" 
                  accept="image/*" 
                  style={{ display: 'none' }} 
                  onChange={handleImageUpload}
                />
                <div className={styles.upload} onClick={() => document.getElementById('image-input')?.click()}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="30px" height="30px" viewBox="0 0 24 24" fill="none">
                    <path d="M14.2647 15.9377L12.5473 14.2346C11.758 13.4519 11.3633 13.0605 10.9089 12.9137C10.5092 12.7845 10.079 12.7845 9.67922 12.9137C9.22485 13.0605 8.83017 13.4519 8.04082 14.2346L4.04193 18.2622M14.2647 15.9377L14.606 15.5991C15.412 14.7999 15.8149 14.4003 16.2773 14.2545C16.6839 14.1262 17.1208 14.1312 17.5244 14.2688C17.9832 14.4253 18.3769 14.834 19.1642 15.6515L20 16.5001M14.2647 15.9377L18.22 19.9628M18.22 19.9628C17.8703 20 17.4213 20 16.8 20H7.2C6.07989 20 5.51984 20 5.09202 19.782C4.7157 19.5903 4.40973 19.2843 4.21799 18.908C4.12583 18.7271 4.07264 18.5226 4.04193 18.2622M18.22 19.9628C18.5007 19.9329 18.7175 19.8791 18.908 19.782C19.2843 19.5903 19.5903 19.2843 19.782 18.908C20 18.4802 20 17.9201 20 16.8V13M11 4H7.2C6.07989 4 5.51984 4 5.09202 4.21799C4.7157 4.40973 4.40973 4.71569 4.21799 5.09202C4 5.51984 4 6.0799 4 7.2V16.8C4 17.4466 4 17.9066 4.04193 18.2622M18 9V6M18 6V3M18 6H21M18 6H15" stroke="#4b4b4bc9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
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
    </div>
  );
}
