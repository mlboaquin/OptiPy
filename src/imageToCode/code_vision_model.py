import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np

class CodeVisionTransformer(nn.Module):
    def __init__(self, vocab_size, max_seq_length=118, d_model=256):
        super().__init__()
        
        # CNN Feature Extractor
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
        )
        
        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=8,
            dim_feedforward=1024,
            dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=6)
        
        # Output layers
        self.fc = nn.Linear(d_model, vocab_size)
        self.max_seq_length = max_seq_length
        
    def forward(self, x):
        # CNN feature extraction
        features = self.cnn(x)
        
        # Reshape for transformer
        batch_size, c, h, w = features.shape
        features = features.permute(0, 2, 3, 1).reshape(batch_size, h * w, c)
        
        # Ensure sequence length matches max_seq_length
        if features.size(1) > self.max_seq_length:
            features = features[:, :self.max_seq_length, :]
        
        # Transformer processing
        output = self.transformer(features)
        
        # Classification
        logits = self.fc(output)
        return logits

class CodeImageDataset(Dataset):
    def __init__(self, image_paths, code_snippets, transform=None, training=True, tokenizer=None, max_length=512):
        self.image_paths = image_paths
        self.code_snippets = code_snippets
        self.base_transform = transform
        self.training = training
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Additional augmentation transforms
        self.augment = transforms.Compose([
            transforms.RandomApply([
                transforms.ColorJitter(
                    brightness=0.2,
                    contrast=0.2,
                    saturation=0.2,
                    hue=0.1
                )
            ], p=0.5),
            transforms.RandomApply([
                transforms.GaussianBlur(kernel_size=3)
            ], p=0.2),
            transforms.RandomAdjustSharpness(sharpness_factor=2, p=0.3),
        ])
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # Load and process image
        image = Image.open(self.image_paths[idx]).convert('RGB')
        
        if self.base_transform:
            image = self.base_transform(image)
        
        if self.training:
            image = self.augment(image)
            
        # Process code snippet
        code = self.code_snippets[idx]
        if self.tokenizer:
            # Tokenize with padding and truncation
            encoded = self.tokenizer.encode(code)
            ids = encoded.ids
            
            # Pad or truncate to max_length
            if len(ids) > self.max_length:
                ids = ids[:self.max_length]
            else:
                # Pad with zeros (assuming 0 is the padding token ID)
                padding_length = self.max_length - len(ids)
                ids = ids + [0] * padding_length
            
            code_tensor = torch.tensor(ids, dtype=torch.long)
        else:
            raise ValueError("Tokenizer not provided to dataset")
        
        return image, code_tensor