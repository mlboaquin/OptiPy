# Code Optimization and Emissions Tracking Project

## Overview

This project is designed to optimize Python code by refactoring it for better energy efficiency and to track the carbon emissions associated with running both the original and optimized code. The application leverages Optical Character Recognition (OCR) to extract code from images, allowing users to input code in various formats. The project is built using Flask for the backend and React with Mantine for the frontend.

## Key Components

### 1. **Backend (Flask)**

The backend is responsible for handling requests, processing code, and tracking emissions. It consists of several key modules:

- **`src/app.py`**: This is the main entry point for the Flask application. It defines the API endpoints for optimizing code, checking the health of the service, and extracting code from images. The `/optimize` endpoint refactors the provided code and measures emissions for both the original and optimized versions.

- **`src/services/code_reformatter.py`**: This module contains the `EnergyEfficientReformatter` class, which uses Python's Abstract Syntax Tree (AST) to refactor code for better energy efficiency. It tracks changes made during the refactoring process and provides feedback on the modifications.

- **`src/services/emissions_tracker.py`**: This module defines the `compare_emissions` function, which measures the carbon emissions and energy consumption of two functions (inefficient and optimized). It uses the `codecarbon` library to track emissions and prints the results for comparison.

- **`src/utils/imageToCode.py`**: This module utilizes Tesseract OCR to extract code from images. It preprocesses the image for better recognition and cleans up the extracted text to ensure it is valid Python code.

### 2. **Frontend (React)**

The frontend is built using React and provides a user-friendly interface for interacting with the backend services.

- **`client/src/App.tsx`**: This is the main application component that sets up routing for the application. It includes routes for the home page and the code calculator, which allows users to input code for optimization.

- **`client/src/components/CodeCalculator.tsx`**: This component provides the interface for users to input their code, submit it for optimization, and view the results, including emissions data.

- **`client/src/components/Home.tsx`**: This component serves as the landing page for the application, providing navigation to the code calculator.

## Features

- **Code Optimization**: Users can submit Python code, which will be refactored for better energy efficiency. The application provides feedback on the changes made during the refactoring process.

- **Emissions Tracking**: The application tracks and compares the carbon emissions and energy consumption of the original and optimized code, providing insights into the environmental impact of code execution.

- **Image to Code Extraction**: Users can upload images containing code, which will be processed using OCR to extract the text and convert it into executable Python code.

- **Health Check Endpoint**: The application includes a health check endpoint to ensure the service is running correctly.

## Installation and Usage

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up the backend**:

   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```
   - Ensure Tesseract OCR is installed and the path is correctly set in `src/utils/imageToCode.py`.

3. **Run the Flask server**:

   ```bash
   python src/app.py
   ```

4. **Set up the frontend**:

   - Navigate to the frontend directory:
     ```bash
     cd client
     ```
   - Install the required Node packages:
     ```bash
     npm install
     ```
   - Start the React application:
     ```bash
     npm start
     ```

5. **Access the application**: Open your web browser and navigate to `http://localhost:5000` to access the application.

## Conclusion

This project aims to promote energy-efficient coding practices by providing tools for code optimization and emissions tracking. By leveraging modern web technologies and machine learning, it offers a unique solution for developers looking to reduce their environmental impact.
