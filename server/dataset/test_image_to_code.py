import os
import json
import sys

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from server.imageToCode import CodeExtractor
from difflib import SequenceMatcher

def load_code_snippets(json_path):
    """Load the ground truth code snippets from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_similarity(text1, text2):
    """Calculate similarity ratio between two text strings"""
    return SequenceMatcher(None, text1, text2).ratio()

def test_code_extraction():
    # Initialize the code extractor
    extractor = CodeExtractor()
    
    # Paths
    test_images_dir = "src/dataset/train/images"
    code_snippets_path = "src/dataset/test/code_snippets.json"
    
    # Debug info
    print(f"Looking for images in: {os.path.abspath(test_images_dir)}")
    if not os.path.exists(test_images_dir):
        print(f"Error: Test images directory does not exist: {test_images_dir}")
        return
        
    image_files = [f for f in os.listdir(test_images_dir) 
                  if f.endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(image_files)} image files: {image_files}")
    
    # Load ground truth code snippets
    if not os.path.exists(code_snippets_path):
        print(f"Error: Code snippets file does not exist: {code_snippets_path}")
        return
    code_snippets = load_code_snippets(code_snippets_path)
    print(f"Loaded {len(code_snippets)} code snippets")
    
    # Track results
    results = []
    total_similarity = 0
    processed_files = 0
    
    # Process each image
    for image_file in image_files:
        # Extract number from filename (remove 'image_' prefix and '.png' suffix)
        image_number = image_file.replace('image_', '').split('.')[0]  # Get number from filename
        print(f"\nProcessing image: {image_file} (number: {image_number})")
        
        if image_number not in code_snippets:
            print(f"Warning: No matching code snippet found for image {image_file}")
            continue
            
        image_path = os.path.join(test_images_dir, image_file)
        
        # Extract code from image
        extracted_code = extractor.extract_code_from_image(image_path)
        if extracted_code is None:
            print(f"Failed to extract code from {image_file}")
            continue
            
        # Get ground truth code
        ground_truth = code_snippets[str(int(image_number)+1)]
        
        # Calculate similarity
        similarity = calculate_similarity(extracted_code, ground_truth)
        total_similarity += similarity
        processed_files += 1
        
        results.append({
            'image': image_file,
            'similarity': similarity,
            'extracted_code': extracted_code,
            'ground_truth': ground_truth
        })
        
        # Print individual result
        print(f"Results for {image_file}:")
        print(f"Similarity score: {similarity:.2%}")
        
        # Print detailed comparison if similarity is below threshold
        if similarity < 0.8:
            print("\nExtracted code:")
            print(extracted_code)
            print("\nGround truth:")
            print(ground_truth)
    
    # Print overall results
    if processed_files > 0:
        average_similarity = total_similarity / processed_files
        print(f"\nOverall Results:")
        print(f"Processed {processed_files} files")
        print(f"Average similarity score: {average_similarity:.2%}")
    else:
        print("\nNo files were processed")
        print("Please ensure that:")
        print("1. The test images directory exists and contains image files")
        print("2. The image filenames match the code snippet keys")
        print("3. The images are in a supported format (.png, .jpg, .jpeg)")

if __name__ == "__main__":
    test_code_extraction()

