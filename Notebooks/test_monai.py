import numpy as np
import torch
from monai.transforms import Compose, Resize, RandRotate, RandZoom, ToTensor

def test_transforms():
    print("Testing transforms with input shape (3, 224, 224)")
    img_chw = np.zeros((3, 224, 224), dtype=np.float32)
    
    transform = Compose([
        Resize((224, 224)),
        RandRotate(range_x=0.15, prob=0.5, keep_size=True),
        RandZoom(min_zoom=0.9, max_zoom=1.1, prob=0.5, keep_size=True),
        ToTensor()
    ])
    
    out_chw = transform(img_chw)
    print("Output shape:", out_chw.shape)
    
if __name__ == "__main__":
    test_transforms()
