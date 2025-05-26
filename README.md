# Code Optimization and Emissions Tracking Project

## Overview

This project is designed to optimize Python code by refactoring it for better energy efficiency and to track the carbon emissions associated with running both the original and optimized code. The application leverages Optical Character Recognition (OCR) to extract code from images, allowing users to input code in various formats. The project is built using Flask for the backend and a static HTML/CSS/JS frontend.

## Project Structure

```
OptiPy/
├── CS Client/          # Computer Science Client Implementation
├── IT Client/          # Information Technology Client Implementation
├── server/            # Server Implementation
├── dataset/           # Training and Test Data
└── test_program/      # Text Processing Programs
```

## Key Components

### 1. **CS Client Implementation**

The CS Client is a standalone implementation that combines both frontend and backend components:

- **`connect.py`**: The main Flask server that handles API requests for code optimization and image-to-code conversion.
- **`imageToCode.py`**: Utilizes Tesseract OCR to extract code from images, with preprocessing for better recognition.
- **`code_reformatter.py`**: Contains the code optimization logic using Python's AST.
- **`emissions_tracker.py`**: Tracks and compares carbon emissions between original and optimized code.
- **`index.html`**: The main user interface.
- **`styles.css`**: Styling for the user interface.
- **`script.js`**: Client-side functionality.

## Features

- **Code Optimization**: Users can submit Python code, which will be refactored for better energy efficiency. The application provides feedback on the changes made during the refactoring process.

- **Emissions Tracking**: The application tracks and compares the carbon emissions and energy consumption of the original and optimized code, providing insights into the environmental impact of code execution.

- **Image to Code Extraction**: Users can upload images containing code, which will be processed using Tesseract OCR to extract the text and convert it into executable Python code.

- **Health Check Endpoint**: The application includes a health check endpoint to ensure the service is running correctly.

## Installation and Usage (CS Client)

### Prerequisites

1. Python 3.x
2. pip (Python package manager)
3. A modern web browser
4. Git
5. Tesseract OCR (installation instructions below)

### Setup Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/mlboaquin/OptiPy.git
   cd OptiPy
   ```

2. **Install Tesseract OCR**:

   **For Mac Users**:

   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install Tesseract
   brew install tesseract
   ```

   **For Windows Users**:

   - Download the Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Run the installer and note the installation path (default: `C:\Program Files\Tesseract-OCR`)
   - Add Tesseract to your system PATH:
     1. Open System Properties > Advanced > Environment Variables
     2. Under System Variables, find and select "Path"
     3. Click "Edit" and add the Tesseract installation path
     4. Click "OK" to save changes

3. **Set up the CS Client environment**:

   ```bash
   cd "CS Client"
   python -m venv venv
   ```

   **For Mac Users**:

   ```bash
   source venv/bin/activate
   ```

   **For Windows Users**:

   ```bash
   .\venv\Scripts\activate
   ```

   Then install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Tesseract Path**:

   **For Mac Users**:

   - Find your Tesseract installation path:
     ```bash
     which tesseract
     ```
   - Update the path in `imageToCode.py` to match your system's Tesseract installation.

   **For Windows Users**:

   - The default path is already set in `imageToCode.py` as `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - If you installed Tesseract in a different location, update the path in `imageToCode.py`

5. **Run the Application**:
   - Start the Flask server:
     ```bash
     python connect.py
     ```
   - Open `index.html` in your web browser

## Using the Application

1. **Input Code**:

   - Type or paste code directly into the input box
   - Upload an image of code using the upload button
   - Click "Optimize" to process your code

2. **View Results**:
   - Optimized code will appear in the output section
   - Changes made will be shown in the "Changes" section
   - Improvement metrics will be displayed in the "Improvement Metrics" section

## Troubleshooting

### Common Issues

1. **Server Won't Start**:

   - Ensure you're in the CS Client directory
   - Verify the virtual environment is activated
   - Check if port 5000 is available

2. **Image-to-Code Not Working**:

   - Verify Tesseract installation
   - Check image quality and format
   - Ensure proper Tesseract path configuration

3. **Module Not Found Errors**:

   - Activate virtual environment
   - Verify all dependencies are installed
   - Check requirements.txt for missing packages

4. **Tesseract Path Issues**:
   - **Windows**: Verify the path in `imageToCode.py` matches your Tesseract installation
   - **Mac**: Ensure Tesseract is properly installed via Homebrew and the path is correctly set

## Conclusion

This project aims to promote energy-efficient coding practices by providing tools for code optimization and emissions tracking. By leveraging OCR technology and energy consumption metrics, it offers a unique solution for developers looking to reduce their environmental impact.

## Contributors

- Boaquin, Mark Lawrence
- Cillado, Aero Micro
- Fajardo, Ma. Betina Julianna C.
- Gabot, Kristian Gerald C.
