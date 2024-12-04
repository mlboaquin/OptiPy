import json
import os

def prepare_tokenizer_training_data(json_path, output_path):
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Read the JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract code snippets and write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        for key, snippet in data.items():
            # Write each snippet on a new line
            f.write(snippet + '\n\n')

if __name__ == "__main__":
    json_path = "src/dataset/train/code_snippets.json"  # Path to your JSON file
    output_path = "src/dataset/tokenizer/training_data.txt"  # Where to save the training data
    prepare_tokenizer_training_data(json_path, output_path)