# Simple Image Compressor

A simple image compression tool that uses a greedy algorithm to compress images while maintaining quality.

## Features
- Compresses JPG, JPEG, PNG, and NEF (Nikon RAW) files
- Adjustable compression threshold
- Real-time preview
- Shows compression ratio and file sizes

## Installation
1. Install Python 3.x
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the program:
```bash
python simple_compressor.py
```
2. Click "Select Image" to choose an image
3. Adjust the threshold slider (lower = more compression)
4. Click "Compress Image" to compress
5. View the results and compressed image

## Requirements
- Python 3.x
- numpy
- Pillow
- rawpy (for NEF files) 