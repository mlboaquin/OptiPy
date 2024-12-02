import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np

class CodeVisionTransformer(nn.Module):
    def __init__(self, vocab_size, max_seq_length=512, d_model=256):
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
        
        # Transformer processing
        output = self.transformer(features)
        
        # Classification
        logits = self.fc(output)
        return logits

class CodeImageDataset(Dataset):
    def __init__(self, image_paths, code_snippets, transform=None):
        self.image_paths = image_paths
        self.code_snippets = code_snippets
        self.transform = transform or transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
        
    def __len__(self):
        return len(self.image_paths)
        
    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx])
        code = self.code_snippets[idx]
        
        if self.transform:
            image = self.transform(image)
            
        return image, code 