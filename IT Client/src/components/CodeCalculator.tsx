import React, { useState, useEffect } from 'react';
import { Textarea, Button, Text, Card, Title, Divider } from '@mantine/core'; // Import Mantine components
import styles from './CodeCalculator.module.css'; // Import CSS module
import axios from 'axios'; // Import axios for making HTTP requests

export default function CodeCalculator() {
  const [code, setCode] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState<any>(null); // State to store the emissions measurement result
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

  const handleUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = event.target.files?.[0] || null;
    setFile(uploadedFile);
    setStatus('Code and file uploaded successfully');
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

  // New function to handle emissions measurement instead of optimization
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
      const { metrics } = response.data;
      setResult({ metrics }); // Store only the metrics result
    } catch (error) {
      setStatus('Error measuring emissions');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearResults = () => {
    setResult(null);
    setStatus('');
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Code Emissions Calculator</h1>
      <div className={styles.textareaGroup}>
        <Textarea
          value={code}
          onChange={(event) => setCode(event.currentTarget.value)}
          placeholder="Enter your code here"
          autosize
          minRows={4}
          className={styles.textarea}
        />
        <div className={styles.buttonGroup}>
          <Button onClick={handlePaste}>Paste</Button>
          <Button onClick={handleDelete} color="red">Delete</Button>
          <Button component="label" className={styles.uploadButton}>
            Upload Image
            <input type="file" hidden onChange={handleImageUpload} />
          </Button>
          <Button onClick={handleMeasure}>Measure</Button>
          <Button onClick={handleClearResults} color="yellow">Clear Results</Button>
        </div>
      </div>
      <Text mt="sm" className={styles.status}>{status}</Text>
      {result && (
        <div className={styles.result}>
          <Title order={2}>Emissions Measurement Result</Title>
          <Divider my="sm" />
          <Card className={styles.resultSection}>
            <Title order={3}>Emissions Metrics:</Title>
            <pre className={styles.metrics}>{JSON.stringify(result.metrics, null, 2)}</pre>
          </Card>
        </div>
      )}
    </div>
  );
}
