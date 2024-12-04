import os
import sys
from pathlib import Path

# Add the project root directory to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Go up three levels from this file
src_path = project_root / "src"
sys.path.append(str(src_path))

# Debug prints
print("Project Root:", project_root)
print("Src Path:", src_path)
print("sys.path:", sys.path)

import torch
from imageToCode.code_extractor import CodeExtractor
import json
import logging

def load_data(train_dir):
    image_paths = []
    code_snippets = []
    
    # Get images from the 'images' subdirectory
    images_dir = os.path.join(train_dir, 'images')
    for filename in os.listdir(images_dir):
        if filename.endswith('.png'):
            image_paths.append(os.path.join(images_dir, filename))
    
    # Get JSON files from the main train directory
    for filename in os.listdir(train_dir):
        if filename.endswith('.json'):
            with open(os.path.join(train_dir, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Iterate over each code snippet in the JSON data
                for key, snippet in data.items():
                    if "...(line too long; chars omitted)" in snippet:
                        logging.warning(f"Truncated code snippet detected in key {key}")
                    code_snippets.append(snippet)
    
    return image_paths, code_snippets

def train_model(train_dir, epochs=10, batch_size=32, model_path="model.pth"):
    # Load data
    image_paths, code_snippets = load_data(train_dir)
    
    # Initialize CodeExtractor
    extractor = CodeExtractor()
    
    # Train the model using CodeExtractor
    extractor.train(image_paths, code_snippets, epochs=epochs, batch_size=batch_size)
    
    # Save the trained model
    extractor.save_model(model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_dir = "C:/Users/user/Desktop/Career/BCS35/Sem_1/Machine Learning/WPH/PROJECT/src/dataset/train"
    train_model(train_dir)