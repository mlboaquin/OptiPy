import os
import json
import shutil
from pathlib import Path
import pandas as pd
from tqdm import tqdm

class CodeDatasetBuilder:
    def __init__(self, output_dir="./dataset"):
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.annotations_file = self.output_dir / "annotations.json"
        
        # Create directories if they don't exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        self.dataset = {
            "images": [],
            "annotations": []
        }
    
    def process_codenet_dataset(self, codenet_path, max_samples=10000):
        """Process IBM Project CodeNet Dataset"""
        codenet_path = Path(codenet_path)
        
        print("Processing CodeNet dataset...")
        python_files = list(codenet_path.glob("**/*.py"))
        for py_file in tqdm(python_files[:max_samples]):
            # Check if corresponding image exists
            img_path = py_file.with_suffix('.png')
            if not img_path.exists():
                continue
                
            # Read code content
            with open(py_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
                
            # Copy image to dataset directory
            new_img_path = self.images_dir / img_path.name
            shutil.copy(img_path, new_img_path)
            
            # Add to dataset
            image_id = len(self.dataset["images"])
            self.dataset["images"].append({
                "id": image_id,
                "file_name": img_path.name
            })
            
            self.dataset["annotations"].append({
                "image_id": image_id,
                "code": code_content
            })
    
    def save_dataset(self):
        """Save the dataset annotations"""
        with open(self.annotations_file, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=2)
        
        print(f"Dataset saved with {len(self.dataset['images'])} samples")
        print(f"Images directory: {self.images_dir}")
        print(f"Annotations file: {self.annotations_file}")
    
    def create_train_val_split(self, val_ratio=0.2):
        """Create train/validation split"""
        df = pd.DataFrame(self.dataset["annotations"])
        
        # Shuffle and split
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        val_size = int(len(df) * val_ratio)
        
        train_df = df[val_size:]
        val_df = df[:val_size]
        
        # Save splits
        train_df.to_json(self.output_dir / "train.json", orient="records", indent=2)
        val_df.to_json(self.output_dir / "val.json", orient="records", indent=2)
        
        print(f"Train samples: {len(train_df)}")
        print(f"Validation samples: {len(val_df)}")

def main():
    builder = CodeDatasetBuilder()
    
    # Process CodeNet dataset
    builder.process_codenet_dataset("path/to/codenet/dataset")
    
    # Save dataset
    builder.save_dataset()
    
    # Create train/val split
    builder.create_train_val_split()

if __name__ == "__main__":
    main() 