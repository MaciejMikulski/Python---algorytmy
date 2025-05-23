import os
from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms
import pandas as pd
import numpy as np

class ImageRecognitionDataset(Dataset):
    def __init__(self, csv_file, image_base_dir, transform=None):
        """
        Args:
            csv_file (str): Path to the CSV file with labels and points.
            image_base_dir (str): Base directory where the images are stored.
            transform (callable, optional): Optional transform to apply to images.
        """
        self.data_frame = pd.read_csv(csv_file)
        self.image_base_dir = image_base_dir
        self.transform = transform

        # Fill missing coordinates with -1
        point_cols = ['X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4', 'Y4']
        self.data_frame[point_cols] = self.data_frame[point_cols].fillna(-1)

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        row = self.data_frame.iloc[idx]

        # Build image path
        filename = row['Filename']
        img_path = os.path.join(self.image_base_dir, filename)
        img_path = os.path.normpath(img_path)

        # Load image (assuming already grayscale)
        image = Image.open(img_path)

        # Apply transform or default ToTensor
        if self.transform:
            image = self.transform(image)
        else:
            image = transforms.ToTensor()(image)  # Converts to shape [1, H, W]

        # Extract label
        label = torch.tensor(row['validMarker'], dtype=torch.float32)

        # Extract points
        point_cols = ['X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4', 'Y4']
        points = torch.tensor(row[point_cols].values.astype(np.float32), dtype=torch.float32)

        return image, label, points