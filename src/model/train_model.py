import torch
from code_extractor import CodeExtractor
import os
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
            with open(os.path.join(train_dir, filename), 'r') as f:
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
    train_dir = "C:/Users/user/Desktop/Career/BCS35/Sem_1/Machine Learning/WPH/PROJECT/src/dataset/train"  # Path to the training data directory

    train_model(train_dir)