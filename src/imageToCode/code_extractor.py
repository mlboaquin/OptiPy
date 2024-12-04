import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from .code_vision_model import CodeVisionTransformer, CodeImageDataset
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace
from PIL import Image
import numpy as np
import torch.optim as optim
import torch.nn.functional as F
from tqdm import tqdm

class CodeExtractor:
    def __init__(self, model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = self._create_tokenizer()
        self.model = None
        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
        
        if model_path:
            self.load_model(model_path)
    
    def _create_tokenizer(self):
        # Initialize the tokenizer
        tokenizer = Tokenizer(BPE(unk_token="[UNK]"))  # Ensure unk_token is set
        trainer = BpeTrainer(special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"])
        tokenizer.pre_tokenizer = Whitespace()

        # Train the tokenizer
        tokenizer.train(files=["C:/Users/user/Desktop/Career/BCS35/Sem_1/Machine Learning/WPH/PROJECT/src/dataset/tokenizer/training_data.txt"], trainer=trainer)

        # Save the tokenizer
        tokenizer.save("C:/Users/user/Desktop/Career/BCS35/Sem_1/Machine Learning/WPH/PROJECT/src/dataset/tokenizer/tokenizer.json")
        return tokenizer
    
    def train(self, image_paths, code_snippets, epochs=100, batch_size=16, validation_split=0.2):
        """Train the model on code screenshot datasets with validation"""
        # Split data into train/val
        n_samples = len(image_paths)
        indices = np.random.permutation(n_samples)
        n_val = int(n_samples * validation_split)
        train_indices = indices[n_val:]
        val_indices = indices[:n_val]
        
        # Create datasets
        train_dataset = CodeImageDataset(
            [image_paths[i] for i in train_indices],
            [code_snippets[i] for i in train_indices],
            self.transform,
            training=True,
            tokenizer=self.tokenizer,
            max_length=512
        )
        val_dataset = CodeImageDataset(
            [image_paths[i] for i in val_indices],
            [code_snippets[i] for i in val_indices],
            self.transform,
            training=False,
            tokenizer=self.tokenizer,
            max_length=512
        )
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Initialize model
        self.model = CodeVisionTransformer(
            vocab_size=self.tokenizer.get_vocab_size(),
            max_seq_length=512,
            d_model=256
        ).to(self.device)
        
        # Initialize optimizer with gradient clipping
        optimizer = optim.AdamW(self.model.parameters(), lr=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5)
        
        # Training loop
        best_val_loss = float('inf')
        patience = 10  # for early stopping
        patience_counter = 0
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            total_train_loss = 0
            train_steps = 0
            
            for batch_idx, (images, codes) in enumerate(tqdm(train_loader)):
                images = images.to(self.device)
                codes = codes.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = F.cross_entropy(outputs.view(-1, outputs.size(-1)), codes.view(-1))
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                loss.backward()
                optimizer.step()
                
                total_train_loss += loss.item()
                train_steps += 1
                
                if batch_idx % 10 == 0:
                    print(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx}, Loss: {loss.item():.4f}")
            
            avg_train_loss = total_train_loss / train_steps
            
            # Validation phase
            self.model.eval()
            total_val_loss = 0
            val_steps = 0
            
            with torch.no_grad():
                for images, codes in val_loader:
                    images = images.to(self.device)
                    codes = codes.to(self.device)
                    
                    outputs = self.model(images)
                    loss = F.cross_entropy(outputs.view(-1, outputs.size(-1)), codes.view(-1))
                    
                    total_val_loss += loss.item()
                    val_steps += 1
            
            avg_val_loss = total_val_loss / val_steps
            
            print(f"Epoch {epoch+1}/{epochs}")
            print(f"Average Training Loss: {avg_train_loss:.4f}")
            print(f"Average Validation Loss: {avg_val_loss:.4f}")
            
            # Learning rate scheduling
            scheduler.step(avg_val_loss)
            
            # Early stopping
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                self.save_model("model_best.pth")
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print("Early stopping triggered")
                    break
    
    def extract_code(self, image_path):
        """Extract code from an image"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
            
        self.model.eval()
        image = Image.open(image_path)
        image = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(image)
            predicted_tokens = torch.argmax(output, dim=-1)
            
        # Decode tokens to text
        decoded = self.tokenizer.decode(predicted_tokens[0].cpu().numpy().tolist())
        return decoded
    
    def save_model(self, path):
        """Save the model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'tokenizer': self.tokenizer
        }, path)
    
    def load_model(self, path):
        """Load the model from disk"""
        checkpoint = torch.load(path)
        self.model = CodeVisionTransformer(
            vocab_size=self.tokenizer.get_vocab_size(),
            max_seq_length=512
        ).to(self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.tokenizer = checkpoint['tokenizer']

def extract_code_from_image(image_path, model_path="models/code_vision_model.pth"):
    """
    Extract code from an image using the trained ML model.
    
    Args:
        image_path (str): Path to the image file (png, jpg, or jpeg)
        model_path (str): Path to the trained model weights
        
    Returns:
        str: Extracted code as a string
    """
    try:
        extractor = CodeExtractor(model_path)
        code = extractor.extract_code(image_path)
        return code
    except Exception as e:
        return f"Error processing image: {str(e)}"