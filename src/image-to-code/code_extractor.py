import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from code_vision_model import CodeVisionTransformer, CodeImageDataset
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace
from PIL import Image

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
        tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
        trainer = BpeTrainer(
            special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]"],
            vocab_size=10000
        )
        return tokenizer
    
    def train(self, image_paths, code_snippets, epochs=10, batch_size=32):
        """Train the model on code screenshot datasets"""
        # Create dataset
        dataset = CodeImageDataset(image_paths, code_snippets, self.transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Initialize model
        self.model = CodeVisionTransformer(
            vocab_size=self.tokenizer.get_vocab_size(),
            max_seq_length=512
        ).to(self.device)
        
        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        # Training loop
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            
            for batch_images, batch_codes in dataloader:
                batch_images = batch_images.to(self.device)
                
                # Tokenize code snippets
                encoded = self.tokenizer.encode_batch(batch_codes)
                targets = torch.tensor([e.ids for e in encoded]).to(self.device)
                
                # Forward pass
                outputs = self.model(batch_images)
                loss = criterion(outputs.view(-1, self.tokenizer.get_vocab_size()), 
                               targets.view(-1))
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")
    
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